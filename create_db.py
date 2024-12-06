import sqlite3

conn = sqlite3.connect('one_piece_tcg.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS card_set (
        set_id TEXT PRIMARY KEY,
        set_name TEXT NOT NULL,
        release_date DATE,
        release_year INTEGER,
        total_cards INTEGER
    )
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS card (
        card_id TEXT PRIMARY KEY,
        Name TEXT,
        Colour TEXT,
        Rarity TEXT,
        Cost INTEGER,
        Power INTEGER,
        card_type TEXT,
        Counter INTEGER,
        set_id TEXT,
        Attribute1 TEXT,
        Attribute2 TEXT,
        Attribute3 TEXT,
        attack_attribute TEXT,
        FOREIGN KEY (set_id) REFERENCES card_set(set_id)
    )
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        user_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS deck (
        deck_id INTEGER PRIMARY KEY,
        deck_name TEXT NOT NULL,
        creator_id INTEGER,
        leader_id TEXT NOT NULL,
        FOREIGN KEY (creator_id) REFERENCES user(user_id),
        FOREIGN KEY (leader_id) REFERENCES card(card_id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_deck (
        user_id INTEGER,
        deck_id INTEGER,
        PRIMARY KEY (user_id, deck_id),
        FOREIGN KEY (user_id) REFERENCES user(user_id),
        FOREIGN KEY (deck_id) REFERENCES deck(deck_id)
    )
""")

conn.commit()
conn.close()