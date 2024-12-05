import sqlite3

conn = sqlite3.connect('one_piece_tcg.db')
cursor = conn.cursor()


#LEADER SHOULD ALSO HAVE LIFE CARD ATTRIBUTES
card_data = [
    ("OP06-114", "Wyper", "Yellow", "UC", 5, 7000, "Character", None, "OP06", "Sky Island", "Shandian Warrior", None, "Ranged"),
    ("OP01-004", "Usopp", "Red", "R", 2, 5000, "Character", 2000, "OP01", "Straw Hat Crew", None, None, "Ranged"),
    ("OP01-005", "Uta", "Red", "R", 4, 4000, "Character", None, "OP01", "Film", None, None, "Special"),
    ("OP01-033", "Izo", "Green", "UC", 3, 3000, "Character", 2000, "OP01", "Land of Wano", "Former WhiteBeard Pirates", None, "Ranged")

]



cursor.execute("UPDATE Card SET set_id = 'OP06' WHERE Name = 'Wyper'")

# Insert the data
cursor.executemany("INSERT OR IGNORE INTO Card (card_id, Name, Colour, Rarity, Cost, Power, card_type, Counter, "
                   "set_id, Attribute1, Attribute2, Attribute3, attack_attribute) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, "
                   "?, ?, ?, ?)", card_data)

# Commit the changes
conn.commit()

# Verify the data was inserted
cursor.execute("SELECT * FROM card")
results = cursor.fetchall()
print("Number of cards in database:", len(results))
for row in results:
    print(row)

conn.close()

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



if __name__ == "__main__":
    # Example usage
    get_card_attributes("OP01-001")