import sqlite3


conn = sqlite3.connect('one_piece_tcg.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE card (
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
        attack_attribute TEXT
        )
""")


conn.commit()
conn.close()
