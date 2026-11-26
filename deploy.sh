#!/usr/bin/env bash
# Update MomentSnap on the server. Run as root on the server: /srv/momentsnap/app/deploy.sh
set -euo pipefail

APP=/srv/momentsnap/app
VENV=/srv/momentsnap/venv
DATA=/srv/momentsnap/data
RUN="sudo -u momentsnap"

cd "$APP"

echo "1/6 Backing up the database"
$RUN sqlite3 "$DATA/db.sqlite3" ".backup '$DATA/backup-$(date +%Y%m%d-%H%M%S).sqlite3'"
ls -1t "$DATA"/backup-*.sqlite3 | tail -n +11 | xargs -r rm --   # keep the 10 newest

echo "2/6 Getting the latest code"
$RUN git pull --ff-only

echo "3/6 Installing requirements"
$RUN "$VENV/bin/pip" install --quiet -r requirements.txt

echo "4/6 Applying migrations"
$RUN "$VENV/bin/python" manage.py migrate --noinput

echo "5/6 Collecting static files"
$RUN "$VENV/bin/python" manage.py collectstatic --noinput

echo "6/6 Restarting the app"
systemctl restart momentsnap

echo "Deployed."