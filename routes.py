from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("Genshin Impact Builds Website.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/teams")
def teams():
    conn = get_db_connection()

    query = """
        SELECT
        Teams.Team_ID,
        Teams.Team_Name,
        Teams.Team_URL,
        C1.Character_ID AS Character_1_ID,
        C1.Character_Name AS Character_1_Name,
        C1.Character_Image_URI AS Character_1_Image_URI,
        C2.Character_ID AS Character_2_ID,
        C2.Character_Name AS Character_2_Name,
        C2.Character_Image_URI AS Character_2_Image_URI,
        C3.Character_ID AS Character_3_ID,
        C3.Character_Name AS Character_3_Name,
        C3.Character_Image_URI AS Character_3_Image_URI,
        C4.Character_ID AS Character_4_ID,
        C4.Character_Name AS Character_4_Name,
        C4.Character_Image_URI AS Character_4_Image_URI
    FROM Teams
    LEFT JOIN Characters C1 ON Teams.Character_ID_1 = C1.Character_ID
    LEFT JOIN Characters C2 ON Teams.Character_ID_2 = C2.Character_ID
    LEFT JOIN Characters C3 ON Teams.Character_ID_3 = C3.Character_ID
    LEFT JOIN Characters C4 ON Teams.Character_ID_4 = C4.Character_ID;
    """

    cur = conn.cursor()
    team_rows = cur.execute(query).fetchall()
    conn.close()

    teams_list = []
    for row in team_rows:
        teams_data = {
            "id": row["Team_ID"],
            "team_name": row["Team_Name"],
            "team_url": row["Team_URL"],
            "characters": [
                {"id": row["Character_1_ID"], "name": row["Character_1_Name"],
                    "image": row["Character_1_Image_URI"]},
                {"id": row["Character_2_ID"], "name": row["Character_2_Name"],
                    "image": row["Character_2_Image_URI"]},
                {"id": row["Character_3_ID"], "name": row["Character_3_Name"],
                    "image": row["Character_3_Image_URI"]},
                {"id": row["Character_4_ID"], "name": row["Character_4_Name"],
                    "image": row["Character_4_Image_URI"]},
            ]
        }
        teams_list.append(teams_data)

    return render_template("teams.html", teams=teams_list)


@app.route("/teams/<string:Team_URL>")
def team(Team_URL):
    conn = get_db_connection()

    query = """
        SELECT
        Teams.Team_ID,
        Teams.Team_Name,
        Teams.Team_URL,

        C1.Character_ID AS Character_1_ID,
        C1.Character_Name AS Character_1_Name,
        C1.Character_Image_URI AS Character_1_Image_URI,
        C1.Character_URL AS Character_1_URL,
        C1.Character_Vision AS Character_1_Vision,
        V1.Vision_Name AS Character_1_Vision_Name,


        C2.Character_ID AS Character_2_ID,
        C2.Character_Name AS Character_2_Name,
        C2.Character_Image_URI AS Character_2_Image_URI,
        C2.Character_URL AS Character_2_URL,
        C2.Character_Vision AS Character_2_Vision,
        V2.Vision_Name AS Character_2_Vision_Name,

        C3.Character_ID AS Character_3_ID,
        C3.Character_Name AS Character_3_Name,
        C3.Character_Image_URI AS Character_3_Image_URI,
        C3.Character_URL AS Character_3_URL,
        C3.Character_Vision AS Character_3_Vision,
        V3.Vision_Name AS Character_3_Vision_Name,

        C4.Character_ID AS Character_4_ID,
        C4.Character_Name AS Character_4_Name,
        C4.Character_Image_URI AS Character_4_Image_URI,
        C4.Character_URL AS Character_4_URL,
        C4.Character_Vision AS Character_4_Vision,
        V4.Vision_Name AS Character_4_Vision_Name

    FROM Teams

    -- Join for Character 1
    INNER JOIN Characters C1 ON Teams.Character_ID_1 = C1.Character_ID
    INNER JOIN Visions V1 ON C1.Character_Vision = V1.Vision_ID

    -- Join for Character 2
    INNER JOIN Characters C2 ON Teams.Character_ID_2 = C2.Character_ID
    INNER JOIN Visions V2 ON C2.Character_Vision = V2.Vision_ID


    -- Join for Character 3
    INNER JOIN Characters C3 ON Teams.Character_ID_3 = C3.Character_ID
    INNER JOIN Visions V3 ON C3.Character_Vision = V3.Vision_ID

    -- Join for Character 4
    INNER JOIN Characters C4 ON Teams.Character_ID_4 = C4.Character_ID
    INNER JOIN Visions V4 ON C4.Character_Vision = V4.Vision_ID
    WHERE Teams.Team_URL = ?
    """

    cur = conn.cursor()

    cur.execute(query, (Team_URL,))
    team_row = cur.fetchone()
    conn.close()
    if team_row is None:
        return render_template("404.html"), 404

    team_data = {
        "id": team_row["Team_ID"],
        "team_name": team_row["Team_Name"],
        "team_url": team_row["Team_URL"],
        "characters": [
            {
                "id": team_row["Character_1_ID"],
                "name": team_row["Character_1_Name"],
                "image": team_row["Character_1_Image_URI"],
                "url": team_row["Character_1_URL"],
                "vision": team_row["Character_1_Vision"],
                "vision_name": team_row["Character_1_Vision_Name"],
            },
            {
                "id": team_row["Character_2_ID"],
                "name": team_row["Character_2_Name"],
                "image": team_row["Character_2_Image_URI"],
                "url": team_row["Character_2_URL"],
                "vision": team_row["Character_2_Vision"],
                "vision_name": team_row["Character_2_Vision_Name"],
            },
            {
                "id": team_row["Character_3_ID"],
                "name": team_row["Character_3_Name"],
                "image": team_row["Character_3_Image_URI"],
                "url": team_row["Character_3_URL"],
                "vision": team_row["Character_3_Vision"],
                "vision_name": team_row["Character_3_Vision_Name"],
            },
            {
                "id": team_row["Character_4_ID"],
                "name": team_row["Character_4_Name"],
                "image": team_row["Character_4_Image_URI"],
                "url": team_row["Character_4_URL"],
                "vision": team_row["Character_4_Vision"],
                "vision_name": team_row["Character_4_Vision_Name"],
            },
        ],
    }

    return render_template("team.html", team=team_data)


@app.route("/characters")
def characters():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM characters ORDER BY Character_Name")
    character_rows = cur.fetchall()
    conn.close()
    characters = [dict(row) for row in character_rows]
    return render_template("characters.html", characters=characters)


@app.route("/characters/<string:Character_URL>")
def character(Character_URL):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM characters WHERE Character_URL = ?",
                (Character_URL,))
    character = cur.fetchone()
    conn.close()
    return render_template("character.html", character=character)


if __name__ == "__main__":
    app.run(debug=True)
