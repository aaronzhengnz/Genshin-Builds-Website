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

    characters_dict = {}
    Team_ID = team_characters[0]["Team_ID"]

    for row in team_characters:
        character_id = row["Character_ID"]

        character_details = {
            "Character_Name": row["Character_Name"],
            "Character_Vision": row["Character_Vision"],
            "Character_Affiliation": row["Character_Affiliation"],
            "Character_Image_URI": row["Character_Image_URI"],
            "Character_URL": row["Character_URL"]
        }

        if character_id not in characters_dict:
            characters_dict[character_id] = character_details

    character_weapon_query = """
    SELECT
        TeamCharacters.Team_ID AS Team_ID,
        TeamCharacters.Character_ID AS Character_ID,
        Weapons.Weapon_ID AS Weapon_ID,
        Weapons.Weapon_Name AS Weapon_Name,
        Weapons.Weapon_Rarity AS Weapon_Rarity,
        WeaponTypes.Weapon_Type_Name AS Weapon_Type,
        Weapons.Weapon_Image_URI AS Weapon_Image_URI,
        CharacterWeapons.Best_In_Slot AS Best_In_Slot,
        CharacterWeapons.Free_To_Play AS Free_To_Play

    FROM TeamCharacters
    INNER JOIN Characters
        ON TeamCharacters.Character_ID = Characters.Character_ID
    INNER JOIN CharacterWeapons
        ON TeamCharacters.Character_ID = CharacterWeapons.Character_ID
    INNER JOIN Weapons
        ON CharacterWeapons.Weapon_ID = Weapons.Weapon_ID
    INNER JOIN WeaponTypes
        ON Weapons.Weapon_Type_ID = WeaponTypes.Weapon_Type_ID

    WHERE TeamCharacters.Team_ID = ?
    """

    cur.execute(character_weapon_query, (Team_ID,))
    character_weapons = cur.fetchall()

    if not character_weapons:
        conn.close()
        return render_template("404.html"), 404

    character_weapon_dict = {}
    for row in character_weapons:
        character_id = row["Character_ID"]

        weapon_details = {
            "Weapon_ID": row["Weapon_ID"],
            "Weapon_Name": row["Weapon_Name"],
            "Weapon_Rarity": row["Weapon_Rarity"],
            "Weapon_Type": row["Weapon_Type"],
            "Weapon_Image_URI": row["Weapon_Image_URI"],
            "Best_In_Slot": row["Best_In_Slot"],
            "Free_To_Play": row["Free_To_Play"]
        }

        if character_id not in character_weapon_dict:
            character_weapon_dict[character_id] = {
                "weapons": [weapon_details]
            }
        else:
            character_weapon_dict[character_id]["weapons"].append(
                weapon_details)

    character_artifact_query = """
    SELECT
        TeamCharacters.Team_ID AS Team_ID,
        TeamCharacters.Character_ID AS Character_ID,
        Characters.Character_Name AS Character_Name,
        ArtifactSet1.Artifact_Set_Name AS Artifact_Set_1,
        ArtifactSet2.Artifact_Set_Name AS Artifact_Set_2,
        FlowerName.Artifact_Piece_Name AS Flower_Name,
        FlowerMainStats.Stat_Name AS Flower_Stat,
        PlumeName.Artifact_Piece_Name AS Plume_Name,
        PlumeMainStats.Stat_Name AS Plume_Stat,
        SandsName.Artifact_Piece_Name AS Sands_Name,
        SandsMainStats.Stat_Name AS Sands_Stat,
        AltSandsName.Artifact_Piece_Name AS AltSands_Name,
        AltSandsMainStats.Stat_Name AS AltSands_Stat,
        GobletName.Artifact_Piece_Name AS Goblet_Name,
        GobletMainStats.Stat_Name AS Goblet_Stat,
        AltGobletName.Artifact_Piece_Name AS AltGoblet_Name,
        AltGobletMainStats.Stat_Name AS AltGoblet_Stat,
        CircletName.Artifact_Piece_Name AS Circlet_Name,
        CircletMainStats.Stat_Name AS Circlet_Stat,
        AltCircletName.Artifact_Piece_Name AS AltCirclet_Name,
        AltCircletMainStats.Stat_Name AS AltCirclet_Stat,
        CharacterArtifacts.Best_In_Slot AS Best_In_Slot

    FROM TeamCharacters
    INNER JOIN Characters
        ON TeamCharacters.Character_ID = Characters.Character_ID
    INNER JOIN CharacterArtifacts
        ON TeamCharacters.Character_ID = CharacterArtifacts.Character_ID
    INNER JOIN RecommendedArtifacts
        ON CharacterArtifacts.Recommended_Artifact_ID =
        RecommendedArtifacts.Recommended_Artifact_ID

    INNER JOIN Artifacts AS Flower
        ON RecommendedArtifacts.Flower_ID = Flower.Artifact_ID
    INNER JOIN Stats AS FlowerMainStats
        ON Flower.MainStat_ID = FlowerMainStats.Stat_ID
    INNER JOIN ArtifactPieces AS FlowerName
        ON Flower.Artifact_Piece_ID = FlowerName.Artifact_Piece_ID

    INNER JOIN Artifacts AS Plume
        ON RecommendedArtifacts.Plume_ID = Plume.Artifact_ID
    INNER JOIN Stats AS PlumeMainStats
        ON Plume.MainStat_ID = PlumeMainStats.Stat_ID
    INNER JOIN ArtifactPieces AS PlumeName
        ON Plume.Artifact_Piece_ID = PlumeName.Artifact_Piece_ID

    INNER JOIN Artifacts AS Sands
        ON RecommendedArtifacts.Sands_ID = Sands.Artifact_ID
    INNER JOIN Stats AS SandsMainStats
        ON Sands.MainStat_ID = SandsMainStats.Stat_ID
    INNER JOIN ArtifactPieces AS SandsName
        ON Sands.Artifact_Piece_ID = SandsName.Artifact_Piece_ID

    LEFT JOIN Artifacts AS AltSands
        ON RecommendedArtifacts.Alternative_Sands_ID = AltSands.Artifact_ID
    LEFT JOIN Stats AS AltSandsMainStats
        ON AltSands.MainStat_ID = AltSandsMainStats.Stat_ID
    LEFT JOIN ArtifactPieces AS AltSandsName
        ON AltSands.Artifact_Piece_ID = AltSandsName.Artifact_Piece_ID

    INNER JOIN Artifacts AS Goblet
        ON RecommendedArtifacts.Goblet_ID = Goblet.Artifact_ID
    INNER JOIN Stats AS GobletMainStats
        ON Goblet.MainStat_ID = GobletMainStats.Stat_ID
    INNER JOIN ArtifactPieces AS GobletName
        ON Goblet.Artifact_Piece_ID = GobletName.Artifact_Piece_ID

    LEFT JOIN Artifacts AS AltGoblet
        ON RecommendedArtifacts.Alternative_Goblet_ID = AltGoblet.Artifact_ID
    LEFT JOIN Stats AS AltGobletMainStats
        ON AltGoblet.MainStat_ID = AltGobletMainStats.Stat_ID
    LEFT JOIN ArtifactPieces AS AltGobletName
        ON AltGoblet.Artifact_Piece_ID = AltGobletName.Artifact_Piece_ID

    INNER JOIN Artifacts AS Circlet
        ON RecommendedArtifacts.Circlet_ID = Circlet.Artifact_ID
    INNER JOIN Stats AS CircletMainStats
        ON Circlet.MainStat_ID = CircletMainStats.Stat_ID
    INNER JOIN ArtifactPieces AS CircletName
        ON Circlet.Artifact_Piece_ID = CircletName.Artifact_Piece_ID

    LEFT JOIN Artifacts AS AltCirclet
        ON RecommendedArtifacts.Alternative_Circlet_ID = AltCirclet.Artifact_ID
    LEFT JOIN Stats AS AltCircletMainStats
        ON AltCirclet.MainStat_ID = AltCircletMainStats.Stat_ID
    LEFT JOIN ArtifactPieces AS AltCircletName
        ON AltCirclet.Artifact_Piece_ID = AltCircletName.Artifact_Piece_ID


    LEFT JOIN ArtifactSets AS ArtifactSet1
        ON RecommendedArtifacts.Artifact_Set_ID_1 =
        ArtifactSet1.Artifact_Set_ID
    LEFT JOIN ArtifactSets AS ArtifactSet2
        ON RecommendedArtifacts.Artifact_Set_ID_2 =
        ArtifactSet2.Artifact_Set_ID

    WHERE TeamCharacters.Team_ID = ?
    """

    cur.execute(character_artifact_query, (Team_ID,))
    character_artifacts = cur.fetchall()

    if not character_artifacts:
        conn.close()
        return render_template("404.html"), 404

    character_artifacts_dict = {}
    for row in character_artifacts:
        character_id = row["Character_ID"]

        artifact_details = {
            "Artifact_Set_Name_1": row["Artifact_Set_1"],
            "Artifact_Set_Name_2": row["Artifact_Set_2"],
            "Flower": {
                "Artifact_Piece_Name": row["Flower_Name"],
                "MainStat": row["Flower_Stat"]
            },
            "Plume": {
                "Artifact_Piece_Name": row["Plume_Name"],
                "MainStat": row["Plume_Stat"]
            },
            "Sands": {
                "Artifact_Piece_Name": row["Sands_Name"],
                "MainStat": row["Sands_Stat"]
            },
            "AltSands": {
                "Artifact_Piece_Name": row["AltSands_Name"],
                "MainStat": row["AltSands_Stat"]
            },
            "Goblet": {
                "Artifact_Piece_Name": row["Goblet_Name"],
                "MainStat": row["Goblet_Stat"]
            },
            "AltGoblet": {
                "Artifact_Piece_Name": row["AltGoblet_Name"],
                "MainStat": row["AltGoblet_Stat"]
            },
            "Circlet": {
                "Artifact_Piece_Name": row["Circlet_Name"],
                "MainStat": row["Circlet_Stat"]
            },
            "AltCirclet": {
                "Artifact_Piece_Name": row["AltCirclet_Name"],
                "MainStat": row["AltCirclet_Stat"]
            },
            "Best_In_Slot": row["Best_In_Slot"]
        }

        if character_id not in character_artifacts_dict:
            character_artifacts_dict[character_id] = {
                "artifacts": [artifact_details]
            }
        else:
            character_artifacts_dict[character_id]["artifacts"].append(
                artifact_details)

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
    """

    cur.execute(character_substats_query, (Team_ID,))
    character_artifacts = cur.fetchall()

    if not character_artifacts:
        conn.close()
        return render_template("404.html"), 404

    character_substats_dict = {}
    for row in character_artifacts:
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

    return render_template("team.html", team=team_dict)


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
