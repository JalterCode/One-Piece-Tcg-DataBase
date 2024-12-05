import requests
from bs4 import BeautifulSoup
import sqlite3
import time


def scrape_set(set_id="OP01", start=1, end=121):
    conn = sqlite3.connect('one_piece_tcg.db')
    cursor = conn.cursor()

    for card_num in range(start, end + 1):
        card_number = f"{card_num:03d}"
        card_id = f"{set_id}-{card_number}"
        card_url = f"/cards/{card_id}"

        print(f"Attempting to scrape card: {card_id}")

        try:
            scrape_single_card(card_url, conn, cursor)
            time.sleep(1)  # Be nice to their server

        except Exception as e:
            print(f"Failed to scrape card {card_id}: {e}")
            continue

    conn.close()


def scrape_single_card(card_url, conn, cursor):
    base_url = f"https://onepiece.limitlesstcg.com{card_url}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(base_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        card_id = card_url.split('/')[-1]
        set_id = card_id.split('-')[0]

        # Get card text section
        card_text = soup.select_one('.card-text')

        # Extract name
        name_elem = card_text.select_one('.card-text-name')
        name = name_elem.text.strip() if name_elem else None

        # Extract type and color
        type_line = card_text.select_one('.card-text-type')
        card_type = None
        color = None
        cost = None
        if type_line:
            spans = type_line.select('span')
            for span in spans:
                if span.get('data-tooltip') == 'Category':
                    card_type = span.text.strip()
                elif span.get('data-tooltip') == 'Color':
                    color = span.text.strip()

            # Extract cost from the type line
            if '• ' in type_line.text:
                cost_text = type_line.text.split('• ')[-1].strip()
                if 'Cost' in cost_text:
                    try:
                        cost = int(cost_text.split()[0])
                    except (ValueError, IndexError):
                        pass

        # Extract power
        power_section = card_text.select('.card-text-section')[1]  # Get the second section
        power = None
        counter = None
        if power_section:
            text = power_section.text.strip()
            if 'Power' in text:
                power_str = text.split('Power')[0].strip()
                try:
                    power = int(power_str.replace(',', ''))
                except ValueError:
                    pass
            if 'Counter' in text:
                counter_str = text.split('+')[1].split()[0]
                try:
                    counter = int(counter_str.replace(',', ''))
                except ValueError:
                    pass

        # Extract rarity
        rarity = None
        rarity_elem = soup.select_one('.prints-current-details')
        if rarity_elem:
            rarity_text = rarity_elem.text.strip()
            if 'Common' in rarity_text:
                rarity = 'C'
            elif 'Uncommon' in rarity_text:
                rarity = 'UC'
            elif 'Rare' in rarity_text:
                rarity = 'R'
            elif 'Super Rare' in rarity_text:
                rarity = 'SR'
            elif 'Secret Rare' in rarity_text:
                rarity = 'SEC'
            elif 'Leader' in rarity_text:
                rarity = 'L'

        # Extract attributes
        attributes = []
        attr_spans = card_text.select('span[data-tooltip="Type"]')
        for span in attr_spans:
            attrs = span.text.strip().split('/')
            attributes.extend(attrs)

        # Ensure we have exactly 3 attributes (pad with None if needed)
        while len(attributes) < 3:
            attributes.append(None)

        # Extract attack attribute
        attack_span = card_text.select_one('span[data-tooltip="Attribute"]')
        attack_attribute = attack_span.text.strip() if attack_span else None

        # Create card data tuple
        card_data = (
            card_id,  # card_id
            name,  # Name
            color,  # Colour
            rarity,  # Rarity
            cost,  # Cost
            power,  # Power
            card_type,  # card_type
            counter,  # Counter
            set_id,  # set_id
            attributes[0],  # Attribute1
            attributes[1],  # Attribute2
            attributes[2],  # Attribute3
            attack_attribute  # attack_attribute
        )

        # Insert into database using passed connection
        cursor.execute("""
            INSERT OR REPLACE INTO card 
            (card_id, Name, Colour, Rarity, Cost, Power, card_type, Counter,
            set_id, Attribute1, Attribute2, Attribute3, attack_attribute)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, card_data)

        conn.commit()
        print(f"Successfully added card: {card_id} - {name}")

    except Exception as e:
        print(f"Error processing card: {e}")


if __name__ == "__main__":
    scrape_set("OP01")