from flask import Flask, redirect, render_template_string
import os
import pymysql

app = Flask(__name__)


def get_connection():
    return pymysql.connect(
        unix_socket=os.environ["DB_UNIX_SOCKET"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        connect_timeout=5,
        cursorclass=pymysql.cursors.DictCursor
    )


@app.route("/viikko2")
@app.route("/viikko2/")
def old_week2_url():
    return redirect("/viikko4/", code=308)


@app.route("/viikko4")
def redirect_to_home():
    return redirect("/viikko4/", code=308)


@app.route("/viikko4/")
def home():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            # Only SELECT is used on Server B.
            cursor.execute("SELECT count FROM visits WHERE id = 1")
            result = cursor.fetchone()

            if result is None:
                raise RuntimeError("Visitor counter row was not found.")

            visits = result["count"]
    finally:
        connection.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Week 4 - Read-only Replica</title>
        <style>
            body {
                background: #101010;
                color: #eeeeee;
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 40px 20px;
                line-height: 1.6;
            }
            main {
                max-width: 850px;
                margin: auto;
            }
            h1, h2, h3 {
                color: #b57aff;
            }
            section {
                background: #202020;
                padding: 25px;
                margin: 20px 0;
                border-radius: 10px;
            }
            .status {
                color: #8ee6a1;
                font-weight: bold;
            }
            .counter {
                font-size: 24px;
                color: #c9a5ff;
                text-align: center;
            }
            .number {
                font-size: 48px;
                display: block;
                font-weight: bold;
            }
            a {
                color: #c9a5ff;
            }
            code {
                color: #d7baff;
                overflow-wrap: anywhere;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                text-align: left;
                padding: 9px;
                border-bottom: 1px solid #444;
                vertical-align: top;
            }
            th {
                color: #c9a5ff;
            }
            .note {
                color: #bbbbbb;
                font-size: 0.95em;
            }
        </style>
    </head>

    <body>
    <main>
        <h1>My Linux Server - Week 4</h1>

        <p class="status">SERVER B — READ-ONLY MARIADB REPLICA</p>

        <p>
            This page displays the visitor counter from Server B's local
            MariaDB database. The database is continuously replicated
            from Server A.
        </p>

        <section>
            <h2>Counter pages</h2>
            <p>
                <a href="http://195.148.20.243/viikko2/">
                    Server A — Week 2 counter (primary)
                </a>
            </p>
            <p>
                <a href="http://86.50.253.51/viikko4/">
                    Server B — Week 4 counter (read-only replica)
                </a>
            </p>
        </section>

        <section>
            <h2>Replicated Visitor Counter</h2>
            <div class="counter">
                <span class="number">{{ visits }}</span>
                Page visits
            </div>
            <p>
                Server role: Replica (Server B)<br>
                Database: Local MariaDB replica<br>
                Application database access: SELECT only
            </p>
            <p>
                Loading or refreshing this page does not increase the
                counter or modify the database. The counter is updated
                through replication from Server A.
            </p>
        </section>

        <section>
            <h2>1. Server setup</h2>
            <table>
                <tr><th>Property</th><th>Server A</th><th>Server B</th></tr>
                <tr>
                    <td>Hostname</td>
                    <td>sennivm</td>
                    <td>sennivmb</td>
                </tr>
                <tr>
                    <td>Public IP</td>
                    <td>195.148.20.243</td>
                    <td>86.50.253.51</td>
                </tr>

                <tr>
                    <td>Operating system</td>
                    <td>Ubuntu 26.04.1 LTS</td>
                    <td>Ubuntu 26.04.1 LTS</td>
                </tr>
                <tr>
                    <td>MariaDB</td>
                    <td>11.8.6</td>
                    <td>11.8.6</td>
                </tr>
                <tr>
                    <td>Database role</td>
                    <td>Primary</td>
                    <td>Read-only replica</td>
                </tr>
            </table>

            <p>
                Server B was created in cPouta using a snapshot of
                Server A. It was assigned its own network addresses.
                MariaDB, replication, the application and the backup
                connection were then configured for the two-server setup.
            </p>
        </section>

        <section>
            <h2>2. Storage layout</h2>

            <h3>Website files and application</h3>
            <ul>
                <li>
                    <code>/var/www/html/</code> on A contains the static
                    website files that are backed up to B.
                </li>
                <li>
                    <code>/opt/viikko2/</code> contains the Flask
                    application on both servers.
                </li>
                <li>
                    <code>/opt/viikko2/venv/</code> contains the Python
                    virtual environment.
                </li>
                <li>
                    <code>/etc/viikko2/db.env</code> contains the
                    database connection settings and credentials.
                    It is not stored in the public website directory
                    or in GitHub.
                </li>
            </ul>

            <h3>Backups on Server B</h3>
            <ul>
                <li>
                    Backup destination:
                    <code>/srv/backups/website/</code>
                </li>
                <li>
                    Each run creates a separate directory named
                    <code>backup-YYYYMMDD-HHMMSS/</code>.
                </li>
                <li>
                    Backup log on A:
                    <code>/var/log/week4-backup.log</code>
                </li>
                <li>
                    Backup script on A:
                    <code>/usr/local/sbin/week4-backup.sh</code>
                </li>
                <li>
                    Cron configuration on A:
                    <code>/etc/cron.d/week4-backup</code>
                </li>
            </ul>

            <p>
                The backup destination is outside
                <code>/var/www/html/</code>, so backup files are not
                publicly served by the web server.
            </p>

            <h3>MariaDB</h3>
            <p>
                MariaDB manages the database files and replication logs
                in its configured data locations. On Server A, binary
                logging uses the
                <code>/var/lib/mariadb/mysqld-bin</code> filename
                prefix. Database replication is separate from the
                website-file backup process.
            </p>
        </section>

        <section>
            <h2>3. Linux users and permissions</h2>
            <ul>
                <li>
                    <code>ubuntu</code> is the administrative Linux
                    account used to manage the servers.
                </li>
                <li>
                    <code>root</code> owns and runs the backup script
                    and its cron job.
                </li>
                <li>
                    <code>www-data</code> runs the Flask/Gunicorn
                    application service.
                </li>
                <li>
                    <code>backupuser</code> is a dedicated account on B
                    used by A for SSH and rsync backups.
                </li>
            </ul>

            <p>
                The backup directory is owned by
                <code>backupuser:backupuser</code> with mode
                <code>750</code>. The backup user's SSH directory has
                mode <code>700</code>, and its
                <code>authorized_keys</code> file has mode
                <code>600</code>.
            </p>
            <p>
                The backup script is owned by root with mode
                <code>750</code>. The backup log is owned by root
                with mode <code>640</code>. The cron configuration
                has mode <code>644</code>.
            </p>
            <p>
                Database credentials are kept in the restricted
                environment file, not in the application source code.
            </p>
        </section>

        <section>
            <h2>4. Database users and replication</h2>
            <p>
                Server A is the MariaDB primary with
                <code>server_id = 1</code>, binary logging enabled
                and row-based binary logging.
            </p>
            <p>
                Server B is the replica with
                <code>server_id = 2</code> and
                <code>read_only = ON</code>. Its application connects
                to its own local MariaDB instance through a Unix socket.
            </p>

            <h3>Database accounts</h3>
            <ul>
                <li>
                    <code>viikko2_app</code> on A is the Week 2
                    application account. It has SELECT and UPDATE
                    permissions on the visitor counter table.
                </li>
                <li>
                    <code>week4_repl</code> is the dedicated replication
                    account on A. It accepts replication connections
                    from B's private IP address.
                </li>
                <li>
                    <code>viikko4_reader</code> on B is the Week 4
                    application account. It has SELECT permission only
                    on <code>viikko2.visits</code>.
                </li>
            </ul>

            <p>
                When the Week 2 page is loaded on A, the application
                increments the visitor counter. MariaDB binary logs
                record the change, and B's replication process applies
                it to B's local database.
            </p>
            <p>
                The Week 4 page only runs a SELECT query. The
                application account cannot update, insert or delete
                records. The replication process can still apply
                changes received from A.
            </p>

            <h3>Why replication is not a replacement for backups</h3>
            <p>
                Replication keeps B's database up to date, but it does
                not preserve historical database versions. An
                accidental update or deletion on A can also be
                replicated to B. Separate timestamped backups provide
                older copies of files that can be restored.
            </p>
        </section>

        <section>
            <h2>5. Hourly website backups</h2>
            <p>
                A cron job runs the backup script every hour, at
                minute zero:
            </p>
            <p><code>0 * * * * root /usr/local/sbin/week4-backup.sh</code></p>
            <p>
                The script uses SSH key authentication and rsync to
                copy <code>/var/www/html/</code> from A to a new
                timestamped directory on B. It records successful
                and failed runs in
                <code>/var/log/week4-backup.log</code>.
            </p>
            <p>
                At least two automatic runs were tested using a
                temporary every-minute cron schedule. The final
                configuration was then changed back to hourly.
            </p>
            <table>
                <tr><th>Run (22 November 2026, UTC)</th><th>Result</th></tr>
                <tr><td>17:46:04</td><td>Manual backup successful</td></tr>
                <tr><td>17:48:02</td><td>Automatic backup successful</td></tr>
                <tr><td>17:49:03</td><td>Automatic backup successful</td></tr>
            </table>
            <p>
                Three timestamped backup directories were verified
                on B:
                <code>backup-20261122-174556</code>,
                <code>backup-20261122-174801</code> and
                <code>backup-20261122-174901</code>.
            </p>
        </section>

        <section>
            <h2>6. Testing and results</h2>
            <table>
                <tr><th>Test</th><th>Result</th></tr>
                <tr>
                    <td>A increments the visitor counter</td>
                    <td>Passed</td>
                </tr>
                <tr>
                    <td>B displays the replicated value</td>
                    <td>Passed; A's value of 20 appeared on B</td>
                </tr>
                <tr>
                    <td>Refreshing B does not increment the counter</td>
                    <td>Passed; the value remained unchanged after two requests</td>
                </tr>
                <tr>
                    <td>B application database permissions</td>
                    <td>Passed; viikko4_reader has SELECT only</td>
                </tr>
                <tr>
                    <td>Automatic backup runs</td>
                    <td>Passed; two automatic successes recorded</td>
                </tr>
                <tr>
                    <td>Restore test</td>
                    <td>Passed; restored file matched the original SHA-256 hash</td>
                </tr>
                <tr>
                    <td>B reboot test</td>
                    <td>Passed; services and replication resumed</td>
                </tr>
            </table>

            <h3>Restore verification</h3>
            <p>
                The file <code>index.html</code> was restored from
                backup <code>backup-20261122-174901</code> to a
                separate test directory on B. Its SHA-256 hash
                matched the original file on A:
            </p>
            <p>
                <code>04c7af10c3ed6907a34a3b5ca60df72b1ebb00dc2359e1728cda0433e1222639</code>
            </p>

            <h3>Replication verification after reboot</h3>
            <ul>
                <li>MariaDB I/O thread: Yes</li>
                <li>MariaDB SQL thread: Yes</li>
                <li>Replication delay: 0 seconds</li>
                <li>Last I/O error: none</li>
                <li>Last SQL error: none</li>
                <li>MariaDB, Nginx, SSH, cron and the application service: active</li>
            </ul>
            <p class="note">
                The public page links above are the submission addresses.
                They should also be checked from a browser outside the
                server environment.
            </p>
        </section>

        <section>
            <h2>7. Problem solved and what I learned</h2>
            <p>
                One important part of the implementation was separating
                the database permissions of the primary application,
                the replication connection and the read-only application
                on B. The Week 4 application can display the replicated
                value without being allowed to change it.
            </p>
            <p>
                I also learned that database replication and file
                backups solve different problems. Replication keeps
                the second database current, while timestamped backups
                allow older file versions to be restored.
            </p>
        </section>

        <section>
            <h2>Source Code and Configuration</h2>
            <p>
                The project repository contains the implementation
                and documentation for this assignment:
            </p>
            <p>
                <a href="https://github.com/paralax10/Linux-Administration/">
                    View the Linux Administration GitHub repository
                </a>
            </p>
            <p class="note">
                Passwords, private SSH keys, database dumps and backup
                archives must not be committed to the repository.
                Replication configuration files should be sanitised.
            </p>
        </section>
    </main>
    </body>
    </html>
    """, visits=visits)
