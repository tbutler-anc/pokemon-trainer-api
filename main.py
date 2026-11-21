# main.py
# Pokémon Trainer API - Week 7 Starter Code
# This file is the foundation of your semester-long project.

from fastapi import FastAPI, HTTPException
# Added during Week 8 Lab
from pydantic import BaseModel
# Added during Week 9 Lab
import sqlite3

# Added during Week 9 Lab
# The name of the database file. SQLite creates it in your project folder
# the first time the program connects to it.
DATABASE = "pokemon.db"


def initialize_database():
    # Connect to the database file and create the trainers table if it
    # does not exist yet. IF NOT EXISTS makes this safe to run every time.
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trainers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        hometown TEXT NOT NULL,
        badges INTEGER NOT NULL,
        favorite_pokemon TEXT NOT NULL
    )
    """)

    # Added During Week 11 Lab
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pokemon_team (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trainer_id INTEGER NOT NULL,
        pokemon_name TEXT NOT NULL,
        pokemon_type TEXT NOT NULL,
        level INTEGER NOT NULL,
        nickname TEXT,
        FOREIGN KEY (trainer_id) REFERENCES trainers(id)
    )
    """)

    conn.commit()
    conn.close()


initialize_database()

# Create the application. Everything else in this file attaches to "app".
app = FastAPI(
    title="Pokémon Trainer API",
    description="A semester-long project API for managing Pokémon Trainers.",
    version="0.1.0",
)

# Temporary "database": a Python list of dictionaries.
# Each dictionary is one trainer. Later this semester, you will replace this
# list with a real SQLite database.
#trainers = [
#    {"id": 1, "name": "Ash Ketchum", "hometown": "Pallet Town", "badges": 8, "favorite_pokemon": "Pikachu"},
#    {"id": 2, "name": "Misty", "hometown": "Cerulean City", "badges": 5, "favorite_pokemon": "Starmie"},
#    {"id": 3, "name": "Brock", "hometown": "Pewter City", "badges": 6, "favorite_pokemon": "Onix"},
#    {"id": 4, "name": "Gary Oak", "hometown": "Pallet Town", "badges": 7, "favorite_pokemon": "Blastoise"},
#]

# The Trainer model describes the information a new trainer must include.
# FastAPI checks every incoming request against this model automatically.
# There is no id field, because your API assigns the id for you.
class Trainer(BaseModel):
    name: str
    hometown: str
    badges: int
    favorite_pokemon: str

# Added During Week 11 Lab
# The Pokemon model describes the information needed to add a Pokémon to a team.
# nickname is optional. If it is left out, it is stored as None.
class Pokemon(BaseModel):
    pokemon_name: str
    pokemon_type: str
    level: int
    nickname: str | None = None


# Endpoint 1: the home page of your API.
# A GET request to "/" returns a welcome message.
@app.get("/")
def read_root():
    return {"message": "Welcome to the Pokémon Trainer API!"}


# Endpoint 2: the full list of trainers.
# A GET request to "/trainers" returns every trainer in the list.
# @app.get("/trainers")
# def get_trainers():
#    return trainers

# Added During Week 9 Lab
@app.get("/trainers")
def get_trainers():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, hometown, badges, favorite_pokemon
        FROM trainers
    """)

    rows = cursor.fetchall()
    conn.close()

    results = []

    for row in rows:
        results.append({
            "id": row[0],
            "name": row[1],
            "hometown": row[2],
            "badges": row[3],
            "favorite_pokemon": row[4]
        })

    return results

# Endpoint 3: one specific trainer.
# {trainer_id} is a path parameter (like the Pokémon name in Week 5).
# FastAPI reads the number from the URL and passes it into the function.
# @app.get("/trainers/{trainer_id}")
# def get_trainer(trainer_id: int):
    # Look through the list for a trainer whose id matches.
#    for trainer in trainers:
#        if trainer["id"] == trainer_id:
#            return trainer

#    # If the loop finishes without finding a match, send back a 404 error.
#    raise HTTPException(status_code=404, detail="Trainer not found")

# Added During Week 9 Lab
@app.get("/trainers/{trainer_id}")
def get_trainer(trainer_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # The ? is a placeholder. SQLite fills it in safely with trainer_id.
    cursor.execute("""
        SELECT id, name, hometown, badges, favorite_pokemon
        FROM trainers
        WHERE id = ?
    """, (trainer_id,))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Trainer not found")

    return {
        "id": row[0],
        "name": row[1],
        "hometown": row[2],
        "badges": row[3],
        "favorite_pokemon": row[4]
    }

# Endpoint 4: create a new trainer.
# A POST request to "/trainers" sends trainer information in the request body.
# status_code=201 means "Created", the correct response when something new is made.
# @app.post("/trainers", status_code=201)
# def create_trainer(trainer: Trainer):
    # Give the new trainer the next id. This works because the ids count up
    # 1, 2, 3... In Lab 9, the database will assign ids for you.
#    new_id = len(trainers) + 1

    # Build a dictionary for the new trainer, using the validated data.
#    new_trainer = {
#        "id": new_id,
#        "name": trainer.name,
#        "hometown": trainer.hometown,
#        "badges": trainer.badges,
#        "favorite_pokemon": trainer.favorite_pokemon,
#    }

    # Add the new trainer to the list and send it back to the client.
#    trainers.append(new_trainer)
#    return new_trainer

# Added During Week 9 Lab
@app.post("/trainers", status_code=201)
def create_trainer(trainer: Trainer):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO trainers
        (name, hometown, badges, favorite_pokemon)
        VALUES (?, ?, ?, ?)
    """, (
        trainer.name,
        trainer.hometown,
        trainer.badges,
        trainer.favorite_pokemon
    ))

    conn.commit()

    # The database assigned the id. lastrowid tells us what it was.
    trainer_id = cursor.lastrowid
    conn.close()

    return {
        "id": trainer_id,
        "name": trainer.name,
        "hometown": trainer.hometown,
        "badges": trainer.badges,
        "favorite_pokemon": trainer.favorite_pokemon
    }

# Added during the Week 10 Lab
# Endpoint 5: update an existing trainer.
# PUT replaces ALL of a trainer's fields, so the request body needs every field.
@app.put("/trainers/{trainer_id}")
def update_trainer(trainer_id: int, trainer: Trainer):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE trainers
        SET
            name = ?,
            hometown = ?,
            badges = ?,
            favorite_pokemon = ?
        WHERE id = ?
    """, (
        trainer.name,
        trainer.hometown,
        trainer.badges,
        trainer.favorite_pokemon,
        trainer_id
    ))

    conn.commit()

    # rowcount is how many rows the UPDATE changed. Zero means no trainer matched.
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Trainer not found")

    cursor.execute("""
        SELECT id, name, hometown, badges, favorite_pokemon
        FROM trainers
        WHERE id = ?
    """, (trainer_id,))

    row = cursor.fetchone()
    conn.close()

    return {
        "id": row[0],
        "name": row[1],
        "hometown": row[2],
        "badges": row[3],
        "favorite_pokemon": row[4]
    }

# Added during Week 10 Lab
# Endpoint 6: delete a trainer.
@app.delete("/trainers/{trainer_id}")
def delete_trainer(trainer_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM trainers
        WHERE id = ?
    """, (trainer_id,))

    conn.commit()

    # If the DELETE removed no rows, no trainer had that id.
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Trainer not found")

    conn.close()

    return {"message": "Trainer deleted successfully"}

# Added During Week 10 Lab
# Endpoint 7: a sample Pokémon team for a trainer (hardcoded for now).
# In Lab 11, the team will come from a database table instead.
# @app.get("/trainers/{trainer_id}/team")
# def get_trainer_team(trainer_id: int):
#    conn = sqlite3.connect(DATABASE)
#    cursor = conn.cursor()
#
#    cursor.execute("""
#        SELECT id
#        FROM trainers
#        WHERE id = ?
#    """, (trainer_id,))
#
#    trainer = cursor.fetchone()
#    conn.close()
#
#    if trainer is None:
#        raise HTTPException(status_code=404, detail="Trainer not found")
#
#    return {
#        "trainer_id": trainer_id,
#        "team": [
#            {"pokemon": "Pikachu", "type": "Electric", "level": 35},
#            {"pokemon": "Charizard", "type": "Fire/Flying", "level": 42},
#            {"pokemon": "Bulbasaur", "type": "Grass/Poison", "level": 28}
#        ]
#    }

#Added Week 11 Lab
@app.get("/trainers/{trainer_id}/team")
def get_trainer_team(trainer_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Verify that the trainer exists.
    cursor.execute("""
        SELECT id
        FROM trainers
        WHERE id = ?
    """, (trainer_id,))

    trainer = cursor.fetchone()

    if trainer is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Trainer not found")

    # Retrieve every Pokémon that belongs to this trainer.
    cursor.execute("""
        SELECT id, pokemon_name, pokemon_type, level, nickname
        FROM pokemon_team
        WHERE trainer_id = ?
    """, (trainer_id,))

    rows = cursor.fetchall()
    conn.close()

    team = []

    for row in rows:
        team.append({
            "id": row[0],
            "pokemon_name": row[1],
            "pokemon_type": row[2],
            "level": row[3],
            "nickname": row[4]
        })

    return {
        "trainer_id": trainer_id,
        "team": team
    }

#Added During Week 11 Lab
# Endpoint 8: add a Pokémon to a trainer's team.
@app.post("/trainers/{trainer_id}/team", status_code=201)
def add_pokemon(trainer_id: int, pokemon: Pokemon):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Verify that the trainer exists.
    cursor.execute("""
        SELECT id
        FROM trainers
        WHERE id = ?
    """, (trainer_id,))

    trainer = cursor.fetchone()

    if trainer is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Trainer not found")

    # Add the Pokémon to the trainer's team.
    cursor.execute("""
        INSERT INTO pokemon_team
        (trainer_id, pokemon_name, pokemon_type, level, nickname)
        VALUES (?, ?, ?, ?, ?)
    """, (
        trainer_id,
        pokemon.pokemon_name,
        pokemon.pokemon_type,
        pokemon.level,
        pokemon.nickname
    ))

    conn.commit()

    # The database assigned the id. lastrowid tells us what it was.
    pokemon_id = cursor.lastrowid
    conn.close()

    return {
        "id": pokemon_id,
        "trainer_id": trainer_id,
        "pokemon_name": pokemon.pokemon_name,
        "pokemon_type": pokemon.pokemon_type,
        "level": pokemon.level,
        "nickname": pokemon.nickname
    }

# Added During Week 11 Lab
# Endpoint 9: remove a Pokémon from a trainer's team.
@app.delete("/trainers/{trainer_id}/team/{pokemon_id}")
def delete_pokemon(trainer_id: int, pokemon_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Verify that the trainer exists.
    cursor.execute("""
        SELECT id
        FROM trainers
        WHERE id = ?
    """, (trainer_id,))

    trainer = cursor.fetchone()

    if trainer is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Trainer not found")

    # Delete the Pokémon, but only if it belongs to THIS trainer.
    cursor.execute("""
        DELETE FROM pokemon_team
        WHERE id = ? AND trainer_id = ?
    """, (pokemon_id, trainer_id))

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Pokémon not found")

    conn.close()

    return {
        "message": f"Pokémon {pokemon_id} was removed from Trainer {trainer_id}'s team."
    }