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
    cur = conn.cursor()

    query = """
        SELECT
        TeamCharacters.Team_ID,
        Team_Name,
        Character_Name,
        Character_Affiliation,
        Team_URL,
        Character_URL,
        Character_Image_URI

        FROM TeamCharacters
        INNER JOIN Teams
            ON TeamCharacters.Team_ID = Teams.Team_ID
        INNER JOIN Characters
            ON TeamCharacters.Character_ID = Characters.Character_ID
    """

    team_rows = cur.execute(query).fetchall()
    conn.close()

    teams_dict = {}

    for row in team_rows:
        team_id = row["Team_ID"]

        character_details = {
            "Character_Name": row["Character_Name"],
            "Character_Affiliation": row["Character_Affiliation"],
            "Character_URL": row["Character_URL"],
            "Character_Image_URI": row["Character_Image_URI"]
        }

        if team_id not in teams_dict:
            teams_dict[team_id] = {
                "Team_Name": row["Team_Name"],
                "Team_URL": row["Team_URL"],
                "Characters": []
            }

        teams_dict[team_id]["Characters"].append(character_details)

    return render_template("teams.html", teams=teams_dict)


@app.route("/teams/<string:Team_URL>")
def team(Team_URL):
    conn = get_db_connection()
    cur = conn.cursor()

    team_character_query = """
        SELECT Teams.Team_Name,
            Characters.Character_Name

        FROM TeamCharacters
        INNER JOIN Teams
            ON TeamCharacters.Team_ID = Teams.Team_ID
        INNER JOIN Characters
            ON TeamCharacters.Character_ID = Characters.Character_ID

        WHERE Teams.Team_URL = ?
    """

    cur.execute(team_character_query, (Team_URL,))
    team_character = cur.fetchone()

    if not team_character:
        conn.close()
        return render_template("404.html"), 404

    team_id = team_character["Team_ID"]

    character_weapons_query = """
        SELECT Characters.Character_Name,
            Weapons.Weapon_Name

        FROM CharacterWeapons
        INNER JOIN Characters
            ON CharacterWeapons.Character_ID = Characters.Character_ID
        INNER JOIN Weapons
            ON CharacterWeapons.Weapon_ID = Weapons.Weapon_ID

        WHERE CharacterWeapons.Team_ID = ?
    """

    cur.execute(character_weapons_query, (team_id,))
    character_weapons = cur.fetchall()

    conn.close()
    if team_character is None:
        return render_template("404.html"), 404

    return render_template("team.html",
                           team_character=team_character,
                           character_weapons=character_weapons)


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
