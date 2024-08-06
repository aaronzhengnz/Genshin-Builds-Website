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

    team_dict = {}

    team_character_query = """
    SELECT
        Teams.Team_ID AS Team_ID,
        Teams.Team_Name AS Team_Name,
        Characters.Character_ID AS Character_ID,
        Characters.Character_Name AS Character_Name,
        Characters.Character_Vision_ID AS Character_Vision_ID,
        Characters.Character_Affiliation AS Character_Affiliation,
        Characters.Character_Image_URI AS Character_Image_URI,
        Characters.Character_URL AS Character_URL,
        Visions.Vision_Name AS Character_Vision

    FROM TeamCharacters
    INNER JOIN Teams
        ON TeamCharacters.Team_ID = Teams.Team_ID
    INNER JOIN Characters
        ON TeamCharacters.Character_ID = Characters.Character_ID
    INNER JOIN Visions
        ON Vision_ID = Characters.Character_Vision_ID

    WHERE Teams.Team_URL = ?
"""

    cur.execute(team_character_query, (Team_URL,))
    team_characters = cur.fetchall()

    if not team_characters:
        conn.close()
        return render_template("404.html"), 404

    Team_ID = team_characters[0]["Team_ID"]

    for row in team_characters:
        character_id = row["Character_ID"]

        character_details = {
            "Character_Name": row["Character_Name"],
            "Character_Vision_ID": row["Character_Vision_ID"],
            "Character_Affiliation": row["Character_Affiliation"],
            "Character_Image_URI": row["Character_Image_URI"],
            "Character_URL": row["Character_URL"]
        }

        if character_id not in team_dict:
            team_dict[character_id] = character_details

    character_weapon_query = """
    SELECT
        Characters.Character_ID AS Character_ID,
        Weapon_ID,
        Best_In_Slot,
        Free_To_Play

    FROM TeamCharacters
    INNER JOIN Characters
        ON TeamCharacters.Character_ID = Characters.Character_ID
    INNER JOIN CharacterWeapons
        ON TeamCharacters.Character_ID = CharacterWeapons.Character_ID

    WHERE TeamCharacters.Team_ID = ?
    """

    cur.execute(character_weapon_query, (Team_ID,))
    character_weapons = cur.fetchall()

    if not character_weapons:
        conn.close()
        return render_template("404.html"), 404

    character_artifact_query = """
    SELECT
        Characters.Character_ID AS Character_ID,
        Recommended_Artifact_ID,
        Best_In_Slot

        FROM TeamCharacters
        INNER JOIN Characters
            ON TeamCharacters.Character_ID = Characters.Character_ID
        INNER JOIN CharacterArtifacts
            ON TeamCharacters.Character_ID = CharacterArtifacts.Character_ID

        WHERE TeamCharacters.Team_ID = ?
    """

    cur.execute(character_artifact_query, (Team_ID,))
    character_artifacts = cur.fetchall()

    return render_template("team.html",
                           team_character=team_dict,
                           aaaa=character_artifacts)


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
