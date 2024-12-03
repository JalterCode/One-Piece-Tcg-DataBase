import sqlite3

conn = sqlite3.connect('one_piece_tcg.db')
cursor = conn.cursor()

card_data = [
    ("OP06-114", "Wyper", "Yellow", "UC", 5, 7000, "Character", None, "OP08", "Sky Island", "Shandian Warrior", None, "Ranged")
]

# Insert the data
cursor.executemany("INSERT INTO Card (card_id, Name, Colour, Rarity, Cost, Power, card_type, Counter, set_id, Attribute1, Attribute2, Attribute3, attack_attribute) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", card_data)

# Commit the changes
conn.commit()

# Verify the data was inserted
cursor.execute("SELECT * FROM card")
results = cursor.fetchall()
print("Number of cards in database:", len(results))
for row in results:
    print(row)

conn.close()