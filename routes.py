from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('Genshin Impact Builds Website.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def Home():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM teams')
    home = cur.fetchall()
    return render_template('home.html', home=home)


@app.route('/teams')
def Teams():
    conn = get_db_connection()

    query = """
        SELECT
        Teams.Team_ID,
        Teams.Team_Name,
        C1.Character_ID AS Character_1_ID,
        C1.Character_Name AS Character_1_Name,
        C2.Character_ID AS Character_2_ID,
        C2.Character_Name AS Character_2_Name,
        C3.Character_ID AS Character_3_ID,
        C3.Character_Name AS Character_3_Name,
        C4.Character_ID AS Character_4_ID,
        C4.Character_Name AS Character_4_Name
    FROM Teams
    LEFT JOIN Characters C1 ON Teams.Character_ID_1 = C1.Character_ID
    LEFT JOIN Characters C2 ON Teams.Character_ID_2 = C2.Character_ID
    LEFT JOIN Characters C3 ON Teams.Character_ID_3 = C3.Character_ID
    LEFT JOIN Characters C4 ON Teams.Character_ID_4 = C4.Character_ID;
    """

    team_rows = conn.execute(query).fetchall()
    conn.close()

    teams_list = []
    for row in team_rows:
        teams_data = {
            "id": row["Team_ID"],
            "team_name": row["Team_Name"],
            "characters": [
                {"id": row["Character_1_ID"], "name": row["Character_1_Name"]},
                {"id": row["Character_2_ID"], "name": row["Character_2_Name"]},
                {"id": row["Character_3_ID"], "name": row["Character_3_Name"]},
                {"id": row["Character_4_ID"], "name": row["Character_4_Name"]},
            ]
        }
        teams_list.append(teams_data)

    return render_template('teams.html', teams=teams_list)


@app.route('/teams/<int:id>')
def Team(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM teams WHERE id = ?', (id,))
    team = cur.fetchone()
    return render_template('team.html', team=team)


if __name__ == "__main__":
    app.run(debug=True)
