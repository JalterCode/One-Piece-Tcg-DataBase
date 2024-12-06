import requests
from bs4 import BeautifulSoup
import json
import time


def scrape_set(set_id="OP01", start=1, end=121):
    cards = []

    for card_num in range(start, end + 1):
        card_number = f"{card_num:03d}"
        card_id = f"{set_id}-{card_number}"
        card_url = f"/cards/{card_id}"

        print(f"Attempting to scrape card: {card_id}")

        try:
            card_data = scrape_single_card(card_url)
            if card_data:
                cards.append(card_data)
            time.sleep(1)  # Be nice to their server

        except Exception as e:
            print(f"Failed to scrape card {card_id}: {e}")
            continue

    # Save all cards to JSON file
    with open(f'{set_id}_cards.json', 'w', encoding='utf-8') as f:
        json.dump(cards, f, indent=4, ensure_ascii=False)


def scrape_single_card(card_url):
    base_url = f"https://onepiece.limitlesstcg.com{card_url}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(base_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        card_data = {
            'card_id': card_url.split('/')[-1],
            'set_id': card_url.split('/')[-1].split('-')[0],
            'name': None,
            'color': None,
            'rarity': None,
            'cost': None,
            'power': None,
            'card_type': None,
            'counter': None,
            'attributes': [],
            'attack_attribute': None
        }

        card_text = soup.select_one('.card-text')
        if card_text:
            # Name
            name_elem = card_text.select_one('.card-text-name')
            card_data['name'] = name_elem.text.strip() if name_elem else None

            # Type, color and cost
            type_line = card_text.select_one('.card-text-type')
            if type_line:
                spans = type_line.select('span')
                for span in spans:
                    if span.get('data-tooltip') == 'Category':
                        card_data['card_type'] = span.text.strip()
                    elif span.get('data-tooltip') == 'Color':
                        card_data['color'] = span.text.strip()

                if '• ' in type_line.text:
                    cost_text = type_line.text.split('• ')[-1].strip()
                    if 'Cost' in cost_text:
                        try:
                            card_data['cost'] = int(cost_text.split()[0])
                        except (ValueError, IndexError):
                            pass

            # Power and Counter
            power_sections = card_text.select('.card-text-section')
            if len(power_sections) > 1:
                power_text = power_sections[1].text.strip()

                # Extract Power
                if 'Power' in power_text:
                    power_str = power_text.split('Power')[0].strip()
                    try:
                        card_data['power'] = int(power_str.replace(',', ''))
                    except ValueError:
                        pass

                # Extract Counter
                if 'Counter' in power_text:
                    counter_parts = power_text.split('+')
                    if len(counter_parts) > 1:
                        counter_str = counter_parts[1].split()[0]
                        try:
                            card_data['counter'] = int(counter_str.replace(',', ''))
                        except ValueError:
                            pass

            # Attributes
            attr_spans = card_text.select('span[data-tooltip="Type"]')
            for span in attr_spans:
                attrs = span.text.strip().split('/')
                card_data['attributes'].extend(attrs)

            # Attack Attribute
            attack_span = card_text.select_one('span[data-tooltip="Attribute"]')
            if attack_span:
                card_data['attack_attribute'] = attack_span.text.strip()

        # Rarity
        rarity_elem = soup.select_one('.prints-current-details')
        if rarity_elem:
            rarity_text = rarity_elem.text.strip()
            if 'Common' in rarity_text:
                card_data['rarity'] = 'C'
            elif 'Uncommon' in rarity_text:
                card_data['rarity'] = 'UC'
            elif 'Super Rare' in rarity_text:
                card_data['rarity'] = 'SR'
            elif 'Secret Rare' in rarity_text:
                card_data['rarity'] = 'SEC'
            elif 'Rare' in rarity_text:
                card_data['rarity'] = 'R'

            elif 'Leader' in rarity_text:
                card_data['rarity'] = 'L'

        print(f"Successfully scraped card: {card_data['card_id']} - {card_data['name']}")
        return card_data

    except Exception as e:
        print(f"Error processing card: {e}")
        return None


if __name__ == "__main__":
    scrape_set("OP07")
    scrape_set("OP08")