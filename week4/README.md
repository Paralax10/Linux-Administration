# Linux Administration — Week 4

## Server information

| Property | Server A | Server B |
|---|---|---|
| Hostname | sennivm | sennivmb |
| Public IP | 195.148.20.243 | 86.50.253.51 |
| Operating system | Ubuntu 26.04.1 LTS | Ubuntu 26.04.1 LTS |
| MariaDB | 11.8.6 | 11.8.6 |
| Role | Primary | Replica |

Server B was created from a snapshot of Server A in cPouta and assigned its own IP addresses. The private network addresses are intentionally omitted from this public repository.

## Public applications

- Server A: http://195.148.20.243/viikko2/
- Server B: http://86.50.253.51/viikko4/

Server A increments the visitor counter. Server B displays the value from its local replicated MariaDB database without modifying it.

## Repository structure

- `backup/week4-backup.sh` — website backup script.
- `cron/week4-backup` — hourly cron configuration.
- `config/server-a-mariadb.cnf` — sanitised MariaDB configuration for A.
- `config/server-b-mariadb.cnf` — sanitised MariaDB configuration for B.
- `server-b/app.py` — Flask application for B.
- `README.md` — this documentation.

## Website backups

A cron job on Server A runs every hour:

`0 * * * * root /usr/local/sbin/week4-backup.sh`

The script copies `/var/www/html/` from A to:

`/srv/backups/website/`

on Server B using rsync over SSH.

Each run creates a timestamped directory named `backup-YYYYMMDD-HHMMSS`.

The script records successful and failed runs in:

`/var/log/week4-backup.log`

It retains the latest 48 backup directories.

Backups are stored outside the public web directory. The destination belongs to the dedicated `backupuser` account. The SSH key is stored separately on Server A and is not included in this repository.

### Backup tests

Three timestamped backups were verified:

- `backup-20261122-174556`
- `backup-20261122-174801`
- `backup-20261122-174901`

The latter two were successful automatic cron runs. The schedule was subsequently changed to hourly.

A restored `index.html` file was compared with the original using SHA-256. Both files had the same hash:

`04c7af10c3ed6907a34a3b5ca60df72b1ebb00dc2359e1728cda0433e1222639`

## MariaDB replication

Server A is the primary:

- `server_id = 1`
- Binary logging enabled.
- Row-based binary logging.
- Bound to its private network address.

Server B is the replica:

- `server_id = 2`
- `read_only = ON`
- Bound to localhost for application access.

A dedicated replication account connects from B to A.

### Database accounts

- `viikko2_app`: application account on A with SELECT and UPDATE permissions on the visitor counter.
- `week4_repl`: dedicated replication account on A.
- `viikko4_reader`: application account on B with SELECT permission only on `viikko2.visits`.

Database credentials are stored in restricted environment files on the servers, not in this repository.

Replication does not replace historical backups. Changes and accidental deletions on the primary can also be replicated to the replica. Timestamped backups provide older file versions for recovery.

## Linux users and permissions

- `ubuntu`: administrative account.
- `root`: owns and runs the backup script and cron job.
- `www-data`: runs the Flask/Gunicorn application.
- `backupuser`: dedicated SSH account for receiving backups on B.

The backup script is owned by root. Its permissions are `750`.
The backup log is owned by root with permissions `640`.
The backup directory belongs to `backupuser` with permissions `750`.
The backup SSH directory has permissions `700`, and `authorized_keys` has permissions `600`.

## Test results

| Test | Result |
|---|---|
| A increments visitor counter | Passed |
| B displays replicated counter | Passed |
| B refresh does not increment counter | Passed |
| B application account has SELECT-only access | Passed |
| Two automatic backup runs | Passed |
| Multiple timestamped backups | Passed |
| Restored file matches original | Passed |
| B services start after reboot | Passed |
| Replication resumes after reboot | Passed |

After rebooting B, MariaDB reported:

- `Slave_IO_Running: Yes`
- `Slave_SQL_Running: Yes`
- `Seconds_Behind_Master: 0`
- No replication I/O or SQL errors.

MariaDB, Nginx, SSH, cron and the Flask application service were all active.

## Problem solved and lessons learned

An issue occurred when shell commands were accidentally included in the Python application file. Gunicorn could not start because the file contained invalid Python syntax. Removing the shell wrapper fixed the problem.

The project also demonstrated why separate database accounts and permissions are important. The replica application can read the visitor counter without being allowed to modify it.

## Security

Private SSH keys, passwords, SQL dumps, backup archives and other credentials must never be committed to this repository. The sanitised configuration files contain settings only, not authentication secrets.
