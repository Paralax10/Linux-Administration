#!/bin/bash

set -u

SOURCE="/var/www/html/"
REMOTE_USER="backupuser"
BACKUP_HOST="SERVER_B_PRIVATE_IP"  # Replace with B's private IP when deploying.
KEY="/home/ubuntu/.ssh/week4_backup"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG="/var/log/week4-backup.log"
REMOTE_DIR="${REMOTE_USER}@${BACKUP_HOST}:/srv/backups/website/backup-${TIMESTAMP}/"

echo "[$(date --iso-8601=seconds)] Starting backup ${TIMESTAMP}" >> "$LOG"

if ssh -i "$KEY" -o IdentitiesOnly=yes "${REMOTE_USER}@${BACKUP_HOST}" \
    "mkdir -p /srv/backups/website/backup-${TIMESTAMP}" \
    && rsync -a --delete -e "ssh -i $KEY -o IdentitiesOnly=yes" \
        "$SOURCE" "$REMOTE_DIR"
then
    echo "[$(date --iso-8601=seconds)] SUCCESS: backup-${TIMESTAMP}" >> "$LOG"

    ssh -i "$KEY" -o IdentitiesOnly=yes "${REMOTE_USER}@${BACKUP_HOST}" \
        'cd /srv/backups/website && ls -1dt backup-* | tail -n +49 | xargs -r rm -rf'
else
    echo "[$(date --iso-8601=seconds)] FAILURE: backup-${TIMESTAMP}" >> "$LOG"
    exit 1
fi
