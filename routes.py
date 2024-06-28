from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('Genshin Impact Builds Website.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def Menu():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM teams')
    menu = cur.fetchall()
    return render_template('menu.html', menu=menu)


@app.route('/teams')
def Teams():
    conn = get_db_connection()
    team_rows = conn.execute('SELECT * FROM teams').fetchall()
    conn.close()

    teams_data = []
    for row in team_rows:
        team = {
            "id": row["Team_ID"],
            "team_name": row["Team_Name"],
            "characters": [
                {"id": row["Character_ID_1"],
                    "name": row["Character_ID_1_Name"]},
                {"id": row["Character_ID_2"],
                    "name": row["Character_ID_2_Name"]},
                {"id": row["Character_ID_3"],
                    "name": row["Character_ID_3_Name"]},
                {"id": row["Character_ID_4"],
                    "name": row["Character_ID_4_Name"]}
            ]
        }
    teams_data.append(team)

    return render_template('teams.html', teams=teams_data)


@app.route('/teams/<int:id>')
def Team(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM teams WHERE id = ?', (id,))
    team = cur.fetchone()
    return render_template('team.html', team=team)


if __name__ == "__main__":
    app.run(debug=True)
