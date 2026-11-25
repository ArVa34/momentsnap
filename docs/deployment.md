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

## Lessons learned

- Check which machine you are on from the prompt before running a command.
- Always test a new login method in a second window before disabling the old one.
