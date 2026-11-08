from flask import Flask, redirect, render_template_string
import sqlite3

app = Flask(__name__)

DATABASE = "/var/lib/viikko2/visitors.sqlite3"


def init_database():
    connection = sqlite3.connect(DATABASE)

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY,
                count INTEGER NOT NULL
            )
        """)

        connection.execute("""
            INSERT OR IGNORE INTO visits (id, count)
            VALUES (1, 0)
        """)

        connection.commit()
    finally:
        connection.close()


init_database()


@app.route("/viikko2")
def redirect_to_home():
    return redirect("/viikko2/", code=308)


@app.route("/viikko2/")
def home():
    connection = sqlite3.connect(DATABASE, timeout=10)

    try:
        connection.execute("""
            UPDATE visits
            SET count = count + 1
            WHERE id = 1
        """)

        connection.commit()

        visits = connection.execute("""
            SELECT count FROM visits WHERE id = 1
        """).fetchone()[0]

    finally:
        connection.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Week 2 - Python Server</title>

        <style>
            body {
                background: #101010;
                color: #eeeeee;
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 40px 20px;
            }

            main {
                max-width: 750px;
                margin: auto;
            }

            h1, h2 {
                color: #b57aff;
            }

            section {
                background: #202020;
                padding: 25px;
                margin: 20px 0;
                border-radius: 10px;
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
        </style>
    </head>

    <body>
        <main>
            <h1>My Linux Server - Week 2</h1>

            <p>
                Welcome to my Python-powered website!
                This application runs on Ubuntu using Flask.
            </p>

            <section>
                <h2>Visitor Counter</h2>

                <div class="counter">
                    <span class="number">{{ visits }}</span>
                    Page visits
                </div>
            </section>

            <section>
                <h2>About the application</h2>
                <p>Python framework: Flask</p>
                <p>Web server: Nginx</p>
                <p>Application server: Gunicorn</p>
                <p>Database: SQLite</p>
            </section>

            <section>
                <h2>Database and persistence</h2>

                <p>
                    The visitor counter is stored in an SQLite database.
                    Every page load increases the counter by one.
                </p>

                <p>
                    The database is stored separately from the
                    application files, so the visitor count survives
                    application and server restarts.
                </p>

                <p>
                    Reboot test: Pending.
                </p>
            </section>

            <section>
                <h2>Source Code</h2>
                <p>
                    <a href="https://github.com/paralax10/Linux-Administration/">
                        View the project on GitHub
                    </a>
                </p>
            </section>

        </main>
    </body>
    </html>
    """, visits=visits)
