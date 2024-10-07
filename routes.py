from flask import Flask, render_template, request, abort
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("Genshin Impact Builds Website.db")
    conn.row_factory = sqlite3.Row
    return conn


# 404 error handler when page is not found can be aborted
@app.errorhandler(404)
def page_not_found(error):
    abort(404)


@app.route("/")  # Home page / lobby page
def home():
    return render_template("home.html")


# Teams page to allow users to view teams
@app.route("/teams", methods=["GET"])
def teams():
    conn = get_db_connection()
    cur = conn.cursor()

    # Query to search for a specific character
    selected_character = request.args.get("query", None)

    teams_query = """
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

    # If a character is selected, filter teams by character
    if selected_character:
        teams_query += """
            WHERE TeamCharacters.Team_ID IN (
                SELECT Team_ID FROM TeamCharacters
                INNER JOIN Characters
                    ON TeamCharacters.Character_ID = Characters.Character_ID
                WHERE Character_Name = ?
            )
        """
        team_rows = cur.execute(teams_query, (selected_character,)).fetchall()
    else:
        team_rows = cur.execute(teams_query).fetchall()

    if not team_rows:
        conn.close()
        abort(404)

    teams_dict = {}  # Dictionary to store teams and their characters

    # Transformation of data retireved from database to make it easier to use
    # in HTML
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

        # Append character details to team
        teams_dict[team_id]["Characters"].append(character_details)

    characters_query = "SELECT * FROM Characters ORDER BY Character_Name"
    character_rows = cur.execute(characters_query).fetchall()

    characters_dict = {}  # Dictionary to store characters

    for row in character_rows:
        character_id = row["Character_ID"]

        character_details = {
            "Character_Name": row["Character_Name"],
            "Character_Affiliation": row["Character_Affiliation"],
            "Character_Image_URI": row["Character_Image_URI"],
        }

        if character_id not in characters_dict:
            characters_dict[character_id] = character_details

    conn.close()
    return render_template("teams.html",
                           teams=teams_dict,
                           characters=characters_dict,
                           selected_character=selected_character)
    # Pass data to HTML


@app.route("/teams/<string:Team_URL>")  # Team page to view team details
def team(Team_URL):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Query to retrieve team details
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
            WeaponTypes.Weapon_Type_Name AS Character_Weapon_Type,
            Visions.Vision_Name AS Character_Vision

        FROM TeamCharacters
        INNER JOIN Teams
            ON TeamCharacters.Team_ID = Teams.Team_ID
        INNER JOIN Characters
            ON TeamCharacters.Character_ID = Characters.Character_ID
        INNER JOIN Visions
            ON Vision_ID = Characters.Character_Vision_ID
        INNER JOIN WeaponTypes
            ON Characters.Character_Weapon_Type_ID = WeaponTypes.Weapon_Type_ID

        WHERE Teams.Team_URL = ?
        """

        cur.execute(team_character_query, (Team_URL,))
        team_characters = cur.fetchall()

        if not team_characters:  # If team is not found, return 404 error
            abort(404)

        characters_dict = {}
        Team_ID = team_characters[0]["Team_ID"]

        for row in team_characters:
            character_id = row["Character_ID"]

            character_details = {
                "Character_Name": row["Character_Name"],
                "Character_Vision": row["Character_Vision"],
                "Character_Affiliation": row["Character_Affiliation"],
                "Character_Image_URI": row["Character_Image_URI"],
                "Character_URL": row["Character_URL"],
                "Character_Weapon_Type": row["Character_Weapon_Type"]
            }

            if character_id not in characters_dict:
                characters_dict[character_id] = character_details

        # Query to retrieve character weapons
        character_weapon_query = """
        SELECT
            TeamCharacters.Team_ID AS Team_ID,
            TeamCharacters.Character_ID AS Character_ID,
            Weapons.Weapon_ID AS Weapon_ID,
            Weapons.Weapon_Name AS Weapon_Name,
            Weapons.Weapon_Rarity AS Weapon_Rarity,
            Weapons.Weapon_Image_URI AS Weapon_Image_URI,
            Weapons.Weapon_URL AS Weapon_URL,
            CharacterWeapons.Best_In_Slot AS Best_In_Slot,
            CharacterWeapons.Free_To_Play AS Free_To_Play

        FROM TeamCharacters
        INNER JOIN Characters
            ON TeamCharacters.Character_ID = Characters.Character_ID
        INNER JOIN CharacterWeapons
            ON TeamCharacters.Character_ID = CharacterWeapons.Character_ID
        INNER JOIN Weapons
            ON CharacterWeapons.Weapon_ID = Weapons.Weapon_ID

        WHERE TeamCharacters.Team_ID = ?
            AND CharacterWeapons.Team_ID = ?
        """

        cur.execute(character_weapon_query, (Team_ID, Team_ID))
        character_weapons = cur.fetchall()

        if not character_weapons:
            abort(404)

        character_weapon_dict = {}
        for row in character_weapons:
            character_id = row["Character_ID"]

            weapon_details = {
                "Weapon_ID": row["Weapon_ID"],
                "Weapon_Name": row["Weapon_Name"],
                "Weapon_Rarity": row["Weapon_Rarity"],
                "Weapon_Image_URI": row["Weapon_Image_URI"],
                "Best_In_Slot": row["Best_In_Slot"],
                "Weapon_URL": row["Weapon_URL"],
                "Free_To_Play": row["Free_To_Play"]
            }

            if character_id not in character_weapon_dict:
                character_weapon_dict[character_id] = {
                    "weapons": [weapon_details]
                }
            else:
                character_weapon_dict[character_id]["weapons"].append(
                    weapon_details)

        # Query to retrieve character artifacts
        character_artifact_query = """
        SELECT
            TeamCharacters.Team_ID AS Team_ID,
            TeamCharacters.Character_ID AS Character_ID,
            Characters.Character_Name AS Character_Name,
            ArtifactSet1.Artifact_Set_Name AS Artifact_Set_1,
            ArtifactSet1.Artifact_Set_URL as Artifact_Set_1_URL,
            ArtifactSet2.Artifact_Set_Name AS Artifact_Set_2,
            ArtifactSet2.Artifact_Set_URL as Artifact_Set_2_URL,
            CharacterArtifacts.Best_In_Slot AS Best_In_Slot,
            ArtifactSet1.Flower_Image_URI AS Artifact_Set_1_Flower_Image_URI,
            ArtifactSet2.Flower_Image_URI AS Artifact_Set_2_Flower_Image_URI

        FROM TeamCharacters
            INNER JOIN Characters
                ON TeamCharacters.Character_ID = Characters.Character_ID
            INNER JOIN CharacterArtifacts
                ON TeamCharacters.Character_ID =
                CharacterArtifacts.Character_ID
                AND TeamCharacters.Team_ID = CharacterArtifacts.Team_ID
            INNER JOIN RecommendedArtifacts
                ON CharacterArtifacts.Recommended_Artifact_ID =
                RecommendedArtifacts.Recommended_Artifact_ID
            INNER JOIN ArtifactSets AS ArtifactSet1
                ON RecommendedArtifacts.Artifact_Set_ID_1 =
                ArtifactSet1.Artifact_Set_ID
            LEFT JOIN ArtifactSets AS ArtifactSet2
                ON RecommendedArtifacts.Artifact_Set_ID_2 =
                ArtifactSet2.Artifact_Set_ID

        WHERE TeamCharacters.Team_ID = ?
            AND CharacterArtifacts.Team_ID = ?;
        """

        cur.execute(character_artifact_query, (Team_ID, Team_ID))
        character_artifacts = cur.fetchall()

        if not character_artifacts:
            abort(404)

        character_artifacts_dict = {}
        for row in character_artifacts:
            character_id = row["Character_ID"]

            artifact_details = {
                "Artifact_Set_Name_1": row["Artifact_Set_1"],
                "Artifact_Set_1_Flower_Image_URI":
                    row["Artifact_Set_1_Flower_Image_URI"],
                "Artifact_Set_1_URL": row["Artifact_Set_1_URL"],
                "Artifact_Set_Name_2": row["Artifact_Set_2"],
                "Artifact_Set_2_Flower_Image_URI":
                    row["Artifact_Set_2_Flower_Image_URI"],
                "Artifact_Set_2_URL": row["Artifact_Set_2_URL"],
                "Best_In_Slot": row["Best_In_Slot"]
            }

            if character_id not in character_artifacts_dict:
                character_artifacts_dict[character_id] = {
                    "artifacts": [artifact_details]
                }
            else:
                character_artifacts_dict[character_id]["artifacts"].append(
                    artifact_details)

        # Query to retrieve character substats
        character_substats_query = """
        SELECT
            TeamCharacters.Team_ID AS Team_ID,
            TeamCharacters.Character_ID AS Character_ID,
            Characters.Character_Name AS Character_Name,
            Stats.Stat_Name AS SubStat_Name,
            CharacterSubStats.Rating AS SubStat_Rating

        FROM TeamCharacters
        INNER JOIN Characters
            ON TeamCharacters.Character_ID = Characters.Character_ID
        INNER JOIN CharacterSubStats
            ON Characters.Character_ID = CharacterSubStats.Character_ID
        INNER JOIN Stats
            ON CharacterSubStats.Stat_ID = Stats.Stat_ID

        WHERE TeamCharacters.Team_ID = ?
            AND CharacterSubStats.Team_ID = ?
        """

        cur.execute(character_substats_query, (Team_ID, Team_ID))
        character_substats = cur.fetchall()

        if not character_substats:
            abort(404)

        character_substats_dict = {}
        for row in character_substats:
            character_id = row["Character_ID"]

            substat_details = {
                "SubStat_Name": row["SubStat_Name"],
                "SubStat_Rating": row["SubStat_Rating"]
            }

            if character_id not in character_substats_dict:
                character_substats_dict[character_id] = {
                    "substats": [substat_details]
                }
            else:
                character_substats_dict[character_id]["substats"].append(
                    substat_details)

        team_dict = {
            "Team_Name": team_characters[0]["Team_Name"],
            "Team_Characters": characters_dict,
            "Character_Weapons": character_weapon_dict,
            "Character_Artifacts": character_artifacts_dict,
            "Character_Substats": character_substats_dict
        }

        # Pass data to HTML
        return render_template("team.html", team=team_dict)

    finally:
        conn.close()  # Ensure the connection is closed after all queries


@app.route("/characters")
def characters():
    # Query to search for a specific character
    query = request.args.get('query', '')
    conn = get_db_connection()
    cur = conn.cursor()

    if query:  # Subquery
        cur.execute("""
                    SELECT * FROM characters WHERE Character_Name LIKE ?
                    ORDER BY Character_Name
                    """, ('%' + query + '%',))
    else:
        cur.execute("SELECT * FROM characters ORDER BY Character_Name")

    character_rows = cur.fetchall()
    conn.close()

    characters = [dict(row) for row in character_rows]
    return render_template("characters.html", characters=characters)


@app.route("/characters/<string:Character_URL>")
def character(Character_URL):
    conn = get_db_connection()
    cur = conn.cursor()

    character_query = """
    SELECT
        Characters.Character_ID AS Character_ID,
        Characters.Character_Name AS Character_Name,
        Visions.Vision_Name AS Character_Vision,
        Characters.Character_Affiliation AS Character_Affiliation,
        Characters.Character_Image_URI AS Character_Image_URI,
        Characters.Character_URL AS Character_URL,
        Characters.Character_Rarity AS Character_Rarity,
        Characters.Character_Splash_Image_URI AS Character_Splash_Image_URI,
        Characters.Character_Description AS Character_Description,
        WeaponTypes.Weapon_Type_Name AS Character_Weapon_Type

    FROM Characters
    INNER JOIN Visions
        ON Characters.Character_Vision_ID = Visions.Vision_ID
    INNER JOIN WeaponTypes
        ON Characters.Character_Weapon_Type_ID = WeaponTypes.Weapon_Type_ID
    WHERE Characters.Character_URL = ?
    """

    cur.execute(character_query, (Character_URL,))
    character = cur.fetchone()

    if not character:   # If character is not found, return 404 error
        conn.close()
        abort(404)

    character_info = {  # Dictionary to store character details
        "Character_ID": character["Character_ID"],
        "Character_Name": character["Character_Name"],
        "Character_Vision": character["Character_Vision"],
        "Character_Affiliation": character["Character_Affiliation"],
        "Character_Image_URI": character["Character_Image_URI"],
        "Character_URL": character["Character_URL"],
        "Character_Rarity": character["Character_Rarity"] * "★",
        "Character_Splash_Image_URI": character["Character_Splash_Image_URI"],
        "Character_Description": character["Character_Description"],
        "Character_Weapon_Type": character["Character_Weapon_Type"]
    }

    # Query to retrieve teams that the character is in
    teams_query = """
    SELECT
        Teams.Team_ID AS Team_ID,
        Teams.Team_Name AS Team_Name,
        Teams.Team_URL AS Team_URL,
        Characters.Character_ID AS Character_ID,
        Characters.Character_Name AS Character_Name,
        Characters.Character_URL AS Character_URL,
        Characters.Character_Image_URI AS Character_Image_URI

    FROM Teams
    INNER JOIN TeamCharacters
        ON Teams.Team_ID = TeamCharacters.Team_ID
    INNER JOIN Characters
        ON TeamCharacters.Character_ID = Characters.Character_ID

    WHERE Teams.Team_ID IN (
        SELECT Teams.Team_ID
        FROM Characters
        INNER JOIN TeamCharacters
            ON Characters.Character_ID = TeamCharacters.Character_ID
        INNER JOIN Teams
            ON TeamCharacters.Team_ID = Teams.Team_ID
        WHERE Characters.Character_URL = ?
    )
    """

    cur.execute(teams_query, (Character_URL,))
    teams = cur.fetchall()

    teams_dict = {}  # Dictionary to store teams that the character is in
    for row in teams:
        team_id = row["Team_ID"]

        if team_id not in teams_dict:
            teams_dict[team_id] = {
                "Team_Name": row["Team_Name"],
                "Team_URL": row["Team_URL"],
                "Characters": []
            }

        character_details = {
            "Character_Name": row["Character_Name"],
            "Character_URL": row["Character_URL"],
            "Character_Image_URI": row["Character_Image_URI"]
        }

        teams_dict[team_id]["Characters"].append(character_details)

    conn.close()
    return render_template("character.html",
                           character=character_info,
                           teams=teams_dict)    # Pass data to HTML


@app.route("/weapons")
def weapons():
    query = request.args.get('query', '')
    conn = get_db_connection()
    cur = conn.cursor()

    if query:
        cur.execute("""
                    SELECT * FROM Weapons WHERE Weapon_Name LIKE ?
                    ORDER BY Weapon_Name
                    """, ('%' + query + '%',))
    else:
        cur.execute("SELECT * FROM Weapons ORDER BY Weapon_Name")

    weapon_rows = cur.fetchall()
    conn.close()

    weapons = [dict(row) for row in weapon_rows]
    return render_template("weapons.html", weapons=weapons)


@app.route("/weapons/<string:Weapon_URL>")
def weapon(Weapon_URL):
    conn = get_db_connection()
    cur = conn.cursor()

    weapon_query = """
    SELECT
        Weapons.Weapon_ID AS Weapon_ID,
        Weapons.Weapon_Name AS Weapon_Name,
        WeaponTypes.Weapon_Type_Name AS Weapon_Type,
        MainStat.Stat_Name AS MainStat,
        Weapons.Weapon_MainStat_Value AS MainStat_Value,
        SubStat.Stat_Name AS SubStat,
        Weapons.Weapon_SubStat_Value AS SubStat_Value,
        Weapons.Weapon_Ability_Name AS Weapon_Ability_Name,
        Weapons.Weapon_Ability AS Weapon_Ability,
        Weapons.Weapon_Rarity AS Weapon_Rarity,
        Weapons.Weapon_Image_URI


    FROM Weapons
    INNER JOIN WeaponTypes
        ON Weapons.Weapon_Type_ID = WeaponTypes.Weapon_Type_ID
    INNER JOIN Stats AS MainStat
        ON Weapons.Weapon_MainStat = MainStat.Stat_ID
    INNER JOIN Stats AS SubStat
        ON Weapons.Weapon_SubStat = SubStat.Stat_ID

    WHERE Weapon_URL = ?
    """

    cur.execute(weapon_query, (Weapon_URL,))
    weapon = cur.fetchone()

    if not weapon:
        conn.close()
        abort(404)

    weapon_info = {
        "Weapon_ID": weapon["Weapon_ID"],
        "Weapon_Name": weapon["Weapon_Name"],
        "Weapon_Type": weapon["Weapon_Type"],
        "MainStat": weapon["MainStat"],
        "MainStat_Value": weapon["MainStat_Value"],
        "SubStat": weapon["SubStat"],
        "SubStat_Value": weapon["SubStat_Value"],
        "Weapon_Ability_Name": weapon["Weapon_Ability_Name"],
        "Weapon_Ability": weapon["Weapon_Ability"],
        "Weapon_Rarity": weapon["Weapon_Rarity"] * "★",
        "Weapon_Image_URI": weapon["Weapon_Image_URI"]
    }

    characters_query = """
    SELECT
        Weapons.Weapon_ID AS Weapon_ID,
        Weapons.Weapon_Name AS Weapon_Name,
        Characters.Character_Name AS Character_Name,
        Characters.Character_Image_URI AS Character_Image_URI,
        Characters.Character_URL AS Character_URL

    FROM Weapons
    INNER JOIN CharacterWeapons
        ON Weapons.Weapon_ID = CharacterWeapons.Weapon_ID
    INNER JOIN Characters
        ON CharacterWeapons.Character_ID = Characters.Character_ID

    WHERE Weapons.Weapon_URL = ?
    """

    cur.execute(characters_query, (Weapon_URL,))
    characters = cur.fetchall()

    # Dictionary to store characters that use the weapon
    characters_dict = {}
    for row in characters:
        character_details = {
            "Character_Name": row["Character_Name"],
            "Character_Image_URI": row["Character_Image_URI"],
            "Character_URL": row["Character_URL"]
        }

        if row["Character_Name"] not in characters_dict:
            characters_dict[row["Character_Name"]] = character_details

    conn.close()
    return render_template("weapon.html",
                           weapon=weapon_info,
                           characters=characters_dict)


@app.route("/artifacts")
def artifacts():
    query = request.args.get('query', '')
    conn = get_db_connection()
    cur = conn.cursor()

    if query:
        cur.execute("""
                    SELECT * FROM ArtifactSets WHERE Artifact_Set_Name LIKE ?
                    ORDER BY Artifact_Set_Name
                    """, ('%' + query + '%',))
    else:
        cur.execute("SELECT * FROM ArtifactSets ORDER BY Artifact_Set_Name")

    artifact_rows = cur.fetchall()
    conn.close()

    artifacts = [dict(row) for row in artifact_rows]
    return render_template("artifacts.html", artifacts=artifacts)


@app.route("/artifacts/<string:Artifact_Set_URL>")
def artifact(Artifact_Set_URL):
    conn = get_db_connection()
    cur = conn.cursor()

    artifact_query = """
    SELECT
        ArtifactSets.Artifact_Set_ID,
        ArtifactSets.Artifact_Set_Name,
        ArtifactSets."2PC_Set_Bonus",
        ArtifactSets."4PC_Set_Bonus",
        ArtifactSets.Flower_Image_URI,
        ArtifactSets.Plume_Image_URI,
        ArtifactSets.Sands_Image_URI,
        ArtifactSets.Goblet_Image_URI,
        ArtifactSets.Circlet_Image_URI,
        Flower_Piece_ID.Artifact_Piece_Name AS Flower_Piece,
        Plume_Piece_ID.Artifact_Piece_Name AS Plume_Piece,
        Sands_Piece_ID.Artifact_Piece_Name AS Sands_Piece,
        Goblet_Piece_ID.Artifact_Piece_Name AS Goblet_Piece,
        Circlet_Piece_ID.Artifact_Piece_Name AS Circlet_Piece,
        ArtifactSets.Artifact_Set_URL

    FROM ArtifactSets
    INNER JOIN ArtifactPieces AS Flower_Piece_ID
        ON ArtifactSets.Flower_Piece_ID = Flower_Piece_ID.Artifact_Piece_ID

    INNER JOIN ArtifactPieces AS Plume_Piece_ID
        ON ArtifactSets.Plume_Piece_ID = Plume_Piece_ID.Artifact_Piece_ID

    INNER JOIN ArtifactPieces AS Sands_Piece_ID
        ON ArtifactSets.Sands_Piece_ID = Sands_Piece_ID.Artifact_Piece_ID

    INNER JOIN ArtifactPieces AS Goblet_Piece_ID
        ON ArtifactSets.Goblet_Piece_ID = Goblet_Piece_ID.Artifact_Piece_ID

    INNER JOIN ArtifactPieces AS Circlet_Piece_ID
        ON ArtifactSets.Circlet_Piece_ID = Circlet_Piece_ID.Artifact_Piece_ID

    WHERE ArtifactSets.Artifact_Set_URL = ?
    """

    cur.execute(artifact_query, (Artifact_Set_URL,))
    artifact_rows = cur.fetchall()

    if not artifact_rows:
        conn.close()
        abort(404)

    # Dictionary to store artifact details for easy access in HTML
    artifacts = {
        "Artifact_Set_ID": artifact_rows[0]["Artifact_Set_ID"],
        "Artifact_Set_Name": artifact_rows[0]["Artifact_Set_Name"],
        "2PC_Set_Bonus": artifact_rows[0]["2PC_Set_Bonus"],
        "4PC_Set_Bonus": artifact_rows[0]["4PC_Set_Bonus"],
        "Flower_Piece": artifact_rows[0]["Flower_Piece"],
        "Plume_Piece": artifact_rows[0]["Plume_Piece"],
        "Sands_Piece": artifact_rows[0]["Sands_Piece"],
        "Goblet_Piece": artifact_rows[0]["Goblet_Piece"],
        "Circlet_Piece": artifact_rows[0]["Circlet_Piece"],
        "Flower_Image_URI": artifact_rows[0]["Flower_Image_URI"],
        "Plume_Image_URI": artifact_rows[0]["Plume_Image_URI"],
        "Sands_Image_URI": artifact_rows[0]["Sands_Image_URI"],
        "Goblet_Image_URI": artifact_rows[0]["Goblet_Image_URI"],
        "Circlet_Image_URI": artifact_rows[0]["Circlet_Image_URI"]
    }

    characters_query = """
    SELECT DISTINCT
        Characters.Character_ID,
        Characters.Character_Name,
        Characters.Character_Image_URI,
        Characters.Character_URL

    FROM ArtifactSets
    INNER JOIN RecommendedArtifacts
        ON ArtifactSets.Artifact_Set_ID =
        RecommendedArtifacts.Artifact_Set_ID_1
    OR
        ArtifactSets.Artifact_Set_ID =
        RecommendedArtifacts.Artifact_Set_ID_2

    INNER JOIN CharacterArtifacts
        ON RecommendedArtifacts.Recommended_Artifact_ID =
        CharacterArtifacts.Recommended_Artifact_ID

    INNER JOIN Characters
        ON CharacterArtifacts.Character_ID = Characters.Character_ID

    WHERE ArtifactSets.Artifact_Set_URL = ?
    """

    cur.execute(characters_query, (Artifact_Set_URL,))
    characters = cur.fetchall()

    # Dictionary to store characters that use the artifact for easy access
    characters_dict = {}
    for row in characters:
        characters_dict[row["Character_ID"]] = {
            "Character_Name": row["Character_Name"],
            "Character_Image_URI": row["Character_Image_URI"],
            "Character_URL": row["Character_URL"]
        }

    conn.close()
    return render_template("artifact.html",
                           artifacts=artifacts,
                           characters=characters_dict)  # Pass data to HTML


if __name__ == "__main__":
    app.run(debug=True)  # Run the Flask app
