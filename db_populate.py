import sqlite3
import json

conn = sqlite3.connect('one_piece_tcg.db')
cursor = conn.cursor()


#LEADER SHOULD ALSO HAVE LIFE CARD ATTRIBUTES
# card_data = [
#     ("OP06-114", "Wyper", "Yellow", "UC", 5, 7000, "Character", None, "OP06", "Sky Island", "Shandian Warrior", None, "Ranged"),
#     ("OP01-004", "Usopp", "Red", "R", 2, 5000, "Character", 2000, "OP01", "Straw Hat Crew", None, None, "Ranged"),
#     ("OP01-005", "Uta", "Red", "R", 4, 4000, "Character", None, "OP01", "Film", None, None, "Special"),
#     ("OP01-033", "Izo", "Green", "UC", 3, 3000, "Character", 2000, "OP01", "Land of Wano", "Former WhiteBeard Pirates", None, "Ranged")
#
# ]


#
# cursor.execute("UPDATE Card SET set_id = 'OP06' WHERE Name = 'Wyper'")
#
# # Insert the data
# cursor.executemany("INSERT OR IGNORE INTO Card (card_id, Name, Colour, Rarity, Cost, Power, card_type, Counter, "
#                    "set_id, Attribute1, Attribute2, Attribute3, attack_attribute) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, "
#                    "?, ?, ?, ?)", card_data)
#
# # Commit the changes
# conn.commit()

# # Verify the data was inserted
# cursor.execute("SELECT * FROM card")
# results = cursor.fetchall()
# print("Number of cards in database:", len(results))
# for row in results:
#     print(row)
#
# conn.close()

def get_card_attributes(card_id):
    conn = sqlite3.connect('one_piece_tcg.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT card_id, Name, Attribute1, Attribute2, Attribute3, attack_attribute 
        FROM card 
        WHERE card_id = ?
    """, (card_id,))

    result = cursor.fetchone()
    conn.close()

    if result:
        print(f"Card: {result[0]} - {result[1]}")
        print(f"Attributes: {result[2]}, {result[3]}, {result[4]}")
        print(f"Attack Attribute: {result[5]}")
    else:
        print(f"No card found with ID: {card_id}")

def delete_deck_data():
    conn = sqlite3.connect('one_piece_tcg.db')
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM deck""")

    cursor.execute("""
    DELETE FROM deck_card""")
    conn.commit()
    conn.close()


def populate_sets():
    conn = sqlite3.connect('one_piece_tcg.db')
    cursor = conn.cursor()

    sets = [
        ('OP01', 'Romance Dawn', '2022-12-02',1, 121),
        ('OP02', 'Paramount War', '2023-03-10',1, 121),
        ('OP03', 'Pillars of Strength', '2023-06-30',1, 121),
        ('OP04', 'Kingdoms of Intrigue', '2023-09-30',1, 121),
        ('OP05', 'Awakening of the New Era', '2023-12-08',2, 121),
        ('OP06', 'Wings of the Captain', '2024-03-15',2, 121),
        ('OP07', '500 Years in the Future', '2024-06-28',2, 121),
        ('OP08', 'Two Legends', '2024-09-13', 2, 121),

    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO card_set (set_id, set_name, release_date, release_year, total_cards)
        VALUES (?, ?, ?, ?, ?)
    """, sets)

    conn.commit()
    conn.close()


def delete_row():
    conn = sqlite3.connect('one_piece_tcg.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS user")


def populate_db_from_json(set_id):
    conn = sqlite3.connect('one_piece_tcg.db')
    cursor = conn.cursor()

    try:
        with open(f'{set_id}_cards.json', 'r', encoding='utf-8') as f:
            cards = json.load(f)

        for card in cards:
            cursor.execute("""
                    INSERT OR REPLACE INTO card 
                    (card_id, Name, Colour, Rarity, Cost, Power, card_type, Counter,
                    set_id, Attribute1, Attribute2, Attribute3, attack_attribute)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                card['card_id'],
                card['name'],
                card['color'],
                card['rarity'],
                card['cost'],
                card['power'],
                card['card_type'],
                card['counter'],
                card['set_id'],
                card['attributes'][0] if len(card['attributes']) > 0 else None,
                card['attributes'][1] if len(card['attributes']) > 1 else None,
                card['attributes'][2] if len(card['attributes']) > 2 else None,
                card['attack_attribute']
            ))

        conn.commit()
        print(f"Successfully populated database from {set_id}_cards.json")

    except Exception as e:
        print(f"Error populating database: {e}")
    finally:
        conn.close()
#When a user creates a deck, they select a leader, the sql queries the data and then only displays
# cards that are from the colors of the leader
if __name__ == "__main__":
    populate_sets()
    # populate_db_from_json("OP01")
    # populate_db_from_json("OP02")
    # populate_db_from_json("OP03")
    # populate_db_from_json("OP04")
    # populate_db_from_json("OP05")
    # populate_db_from_json("OP06")
    # populate_db_from_json("OP07")
    # populate_db_from_json("OP08")