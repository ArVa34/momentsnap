# MomentSnap deployment notes

Server: Hostinger VPS (KVM 1), Ubuntu 24.04 LTS, domain momentsnap.eu.
No passwords, keys or IP addresses are written in this file.

## 1. Server security (Step 8a)

- Log in with an SSH key instead of a password.
- Firewall (ufw): only ports 22 (SSH), 80 (HTTP) and 443 (HTTPS) are open.
- fail2ban blocks IP addresses that guess passwords.
- Automatic security updates (unattended-upgrades).

## 2. Folders on the server

- /srv/momentsnap/app the code, cloned from GitHub
- /srv/momentsnap/venv Python virtual environment
- /srv/momentsnap/data SQLite database (outside the code folder)
- /srv/momentsnap/static CSS/JS collected by collectstatic
- /srv/momentsnap/media uploaded images

## 3. Application setup (Step 8b)

- Installed: python3-venv, python3-dev, git, nginx, sqlite3.
- Created a system user "momentsnap" that cannot log in; the app runs as this user.
- Cloned the repo into /srv/momentsnap/app and set the owner to momentsnap.
- Created the venv and installed requirements.txt.
- Created .env with production values (DEBUG=False, a new SECRET_KEY,
  ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, paths for the database, static and media).
  Permissions 600, so only the app user can read it.
- Ran: check --deploy, migrate, collectstatic, createsuperuser.

## 4. Test

- Started Gunicorn on 127.0.0.1:8000 (only reachable inside the server).
- curl with Host: momentsnap.eu returned 200; without the Host header it returned 400
  (ALLOWED_HOSTS rejects unknown addresses).

## 5. Gunicorn as a permanent service (Step 8c)

Gunicorn runs the Django app. systemd (Linux's service manager) starts it at boot
and restarts it if it crashes.

File: `/etc/systemd/system/momentsnap.service`

```ini
[Unit]
Description=MomentSnap (Gunicorn)
After=network.target

[Service]
User=momentsnap
Group=momentsnap
WorkingDirectory=/srv/momentsnap/app
ExecStart=/srv/momentsnap/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 config.wsgi
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

- Runs as the `momentsnap` user, never as root.
- 3 workers (rule of thumb: 2 x CPUs + 1), so several visitors are served at once.
- Listens only on 127.0.0.1, so it can be reached only from inside the server (through Nginx).

Commands: `systemctl daemon-reload`, `systemctl enable --now momentsnap`, `systemctl status momentsnap`.

## 6. Nginx: the front door

File: `/etc/nginx/sites-available/momentsnap`, linked into `sites-enabled`.
The default Nginx site was removed.

| Part                                          | What it does                                                                        |
| --------------------------------------------- | ----------------------------------------------------------------------------------- |
| `server_name momentsnap.eu www.momentsnap.eu` | Which addresses this configuration answers                                          |
| `server_tokens off`                           | Hides the Nginx version from visitors and attackers                                 |
| `client_max_body_size 10M`                    | Refuses uploads over 10 MB (Django's own limit is 5 MB)                             |
| `location ~ /\.` with `deny all`              | Folder security: hidden files such as `.env` and `.git` return 403                  |
| `location /static/`                           | Serves CSS/JS directly from `/srv/momentsnap/static` (fast, no Django)              |
| `location /media/` + `nosniff`                | Serves uploaded images; browsers may not treat them as scripts                      |
| `location /`                                  | Passes everything else to Gunicorn, with the `Host` and `X-Forwarded-Proto` headers |

Directory listing is off by default, so nobody can browse the folders.
Permissions: `/srv/momentsnap` is 755 (Nginx can reach static and media);
`/srv/momentsnap/data` is 700 (only the app user can open the database).

Always test before reloading: `nginx -t`, then `systemctl reload nginx`.

## 7. HTTPS with Let's Encrypt (Certbot)

- Installed `certbot` and `python3-certbot-nginx`.
- `certbot --nginx -d momentsnap.eu -d www.momentsnap.eu` obtained a free certificate,
  added HTTPS to the Nginx file and a redirect from HTTP to HTTPS.
- Certificates last 90 days; a systemd timer renews them automatically.
  Checked with `certbot renew --dry-run`.

## 8. Redirects

- HTTP to HTTPS: added by Certbot (301).
- www to the main address: added in the HTTPS server block:

```nginx
if ($host = www.momentsnap.eu) {
    return 301 https://momentsnap.eu$request_uri;
}
```

`301` means "moved permanently"; `$request_uri` keeps the page path.
The HTTP block also sends `http://www...` straight to `https://momentsnap.eu` (one redirect, not two).

## 9. Django's HTTPS settings

Switched on with `DJANGO_HTTPS=True` in the server's `.env`, only after the certificate existed,
because forcing HTTPS earlier would have made the site unreachable.

- `SECURE_PROXY_SSL_HEADER`: Django trusts Nginx's `X-Forwarded-Proto` header to know the visitor used HTTPS.
- `SECURE_SSL_REDIRECT`: any HTTP request is redirected to HTTPS.
- `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`: login and CSRF cookies are only sent over HTTPS.
- `SECURE_HSTS_SECONDS = 3600`: browsers remember to use only HTTPS for one hour.
  It will be raised to one year once the site is stable. Starting small means a mistake can't lock visitors out for a year.
- `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`: safe because we control the whole domain.

### HSTS preload decision

`SECURE_HSTS_PRELOAD` is deliberately not used, and the warning `security.W021` is silenced
in `settings.py` with a comment. Being added to the browsers' built-in preload list is very hard
to undo, so it is not suitable for a new site.

### Secret key

The production server has its own 50-character secret key, different from the development one.
A first attempt left a weak key in `.env`; `check --deploy` caught it (warning W009) and it was replaced.

## 10. Verification

- `manage.py check --deploy`: "System check identified no issues (1 silenced)."
- `curl -sI http://momentsnap.eu` returns 301 to https://momentsnap.eu/
- `curl -sI https://www.momentsnap.eu/shop/` returns 301 to https://momentsnap.eu/shop/
- `curl -sI https://momentsnap.eu/.env` returns 403 Forbidden
- Response headers include `Strict-Transport-Security: max-age=3600; includeSubDomains`,
  `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, and `Server: nginx` with no version.

## More lessons learned

- Run `manage.py` from `/srv/momentsnap/app`, not from root's home folder:
  the app user is not allowed into `/root`, so commands fail with "Permission denied".
- When a block of commands starts with `ssh`, run that line alone and wait for the server prompt.
- `check
