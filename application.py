from flask import Flask, render_template, request, redirect, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'lol'

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect('one_piece_tcg.db')
    cursor = conn.cursor()

    selected_color = None
    selected_cost = None
    selected_set = None
    selected_rarity = None
    selected_counter = None
    selected_card_type = None
    selected_year = None
    if request.method == 'POST':
        selected_color = request.form.get('color')
        selected_cost = request.form.get('cost')
        selected_set = request.form.get('set')
        selected_rarity = request.form.get('rarity')
        selected_counter = request.form.get('counter')
        selected_card_type = request.form.get('card_type')
        selected_year = request.form.get('year')

        query = """
                   SELECT c.* 
                   FROM card c
                   JOIN card_set cs ON c.set_id = cs.set_id 
                   WHERE 1=1
               """
        year_query = 'SELECT'
        params = []
        if selected_color:
            query += ' AND (Colour = ? OR Colour LIKE ? OR Colour LIKE ?)'
            params.extend([selected_color, f"{selected_color}/%", f"%/{selected_color}"])
        if selected_cost:
            query += ' AND Cost = ?'
            params.append(selected_cost)
        if selected_set:
            query += ' And set_id = ?'
            params.append(selected_set)
        if selected_rarity:
            query += ' And Rarity = ?'
            params.append(selected_rarity)
        if selected_counter:
            if selected_counter.lower() == "null":
                query += ' AND Counter IS NULL'
            else:
                query += ' AND Counter = ?'
                params.append(selected_counter)
        if selected_card_type:
            query += ' And card_type = ?'
            params.append(selected_card_type)
        if selected_year:
            query += ' And cs.release_year = ?'
            params.append(selected_year)
        cursor.execute(query, params)
    else:
        cursor.execute('SELECT * FROM Card')

    cards = cursor.fetchall()
    conn.close()

    return render_template('index.html',
                           cards=cards,
                           selected_color=selected_color,
                           selected_cost=selected_cost,
                           selected_set=selected_set,
                           selected_rarity=selected_rarity,
                           selected_counter=selected_counter,
                           selected_card_type=selected_card_type,
                           selected_year=selected_year
                           )


@app.route('/create_deck', methods=['POST'])
def create_deck():
    if request.method == 'POST':
        deck_name = request.form.get('deck_name')
        leader_id = request.form.get('leader_id')
        creator_id = session.get('user_id', 1)  # Use selected user or default to 1

        conn = sqlite3.connect('one_piece_tcg.db')
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO deck (deck_name, leader_id, creator_id)
            VALUES (?, ?, ?)
        """, (deck_name, leader_id, creator_id))

        deck_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return redirect(f'/deck/{deck_id}/build')


@app.route('/decks')
def decks():
    conn = sqlite3.connect('one_piece_tcg.db')
    cursor = conn.cursor()

    # Get current user_id from session
    current_user_id = session.get('user_id')

    # Get all users for the dropdown
    cursor.execute("SELECT user_id, username FROM user ORDER BY username")
    users = cursor.fetchall()

    # Get all leaders for deck creation
    cursor.execute("""
        SELECT card_id, Name, Colour 
        FROM card 
        WHERE card_type = 'Leader'
        ORDER BY Name
    """)
    leaders = cursor.fetchall()

    # Get decks created by or added to user's collection
    cursor.execute("""
        SELECT DISTINCT d.deck_id, d.deck_name, d.creator_id, 
               c.Name as leader_name, c.Colour as leader_color,
               u.username as creator_name,
               (SELECT SUM(quantity) FROM deck_card WHERE deck_id = d.deck_id) as card_count,
               CASE 
                   WHEN d.creator_id = ? THEN 'Created by you'
                   ELSE 'Added to collection'
               END as deck_status
        FROM deck d
        JOIN card c ON d.leader_id = c.card_id
        JOIN user u ON d.creator_id = u.user_id
        LEFT JOIN user_deck ud ON d.deck_id = ud.deck_id
        WHERE d.creator_id = ? OR ud.user_id = ?
        ORDER BY d.deck_name
    """, (current_user_id, current_user_id, current_user_id))

    decks = cursor.fetchall()

    conn.close()

    return render_template('decks.html',
                           users=users,
                           current_user_id=current_user_id,
                           leaders=leaders,
                           decks=decks,
                           active_tab='decks')

@app.route('/deck/<int:deck_id>/build')
def build_deck(deck_id):
    conn = sqlite3.connect('one_piece_tcg.db')
    cursor = conn.cursor()

    # Get deck and leader info
    cursor.execute("""
        SELECT d.*, c.Name, c.Colour
        FROM deck d
        JOIN card c ON d.leader_id = c.card_id
        WHERE d.deck_id = ?
    """, (deck_id,))
    deck = cursor.fetchone()

    # Get leader's colors
    leader_color = deck[5]  # Assuming color is at index 5
    colors = leader_color.split('/')

    # Get available cards matching leader's colors
    color_conditions = ' OR '.join(['Colour LIKE ?' for _ in colors])
    params = [f'%{color}%' for color in colors]
    cursor.execute(f"""
        SELECT DISTINCT c.*
        FROM card c
        WHERE c.card_type != 'Leader'
        AND ({color_conditions})
        ORDER BY c.Name
    """, params)
    available_cards = cursor.fetchall()

    # Get current deck cards
    cursor.execute("""
        SELECT c.*, dc.quantity
        FROM card c
        JOIN deck_card dc ON c.card_id = dc.card_id
        WHERE dc.deck_id = ?
    """, (deck_id,))

    deck_cards = cursor.fetchall()

    conn.close()
    return render_template('deck_builder.html',
                           deck=deck,
                           available_cards=available_cards,
                           deck_cards=deck_cards)


@app.route('/deck/<int:deck_id>/add_card', methods=['POST'])
def add_card_to_deck(deck_id):
    card_id = request.form.get('card_id')
    quantity = int(request.form.get('quantity', 1))

    conn = sqlite3.connect('one_piece_tcg.db')
    cursor = conn.cursor()

    # Check if card already exists in deck
    cursor.execute("""
        SELECT quantity FROM deck_card
        WHERE deck_id = ? AND card_id = ?
    """, (deck_id, card_id))
    existing = cursor.fetchone()

    if existing:
        new_quantity = min(existing[0] + quantity, 4)
        cursor.execute("""
            UPDATE deck_card
            SET quantity = ?
            WHERE deck_id = ? AND card_id = ?
        """, (new_quantity, deck_id, card_id))
    else:
        cursor.execute("""
            INSERT INTO deck_card (deck_id, card_id, quantity)
            VALUES (?, ?, ?)
        """, (deck_id, card_id, min(quantity, 4)))

    conn.commit()
    conn.close()

    return redirect(f'/deck/{deck_id}/build')


@app.route('/deck/<int:deck_id>/save', methods=['POST'])
def save_deck(deck_id):
    conn = sqlite3.connect('one_piece_tcg.db')
    cursor = conn.cursor()

    # Get total card count
    cursor.execute("""
        SELECT SUM(quantity)
        FROM deck_card
        WHERE deck_id = ?
    """, (deck_id,))
    total_cards = cursor.fetchone()[0] or 0

    # Validate deck has exactly 50 cards
    if total_cards != 50:
        flash('Deck must contain exactly 50 cards.')
        return redirect(f'/deck/{deck_id}/build')

    conn.commit()
    conn.close()

    return redirect('/decks')


@app.route('/view_decks')
def view_decks():
    conn = sqlite3.connect('one_piece_tcg.db')
    cursor = conn.cursor()

    current_user_id = session.get('user_id')

    cursor.execute("""
        SELECT d.deck_id, d.deck_name, c.Name as leader_name, c.Colour as leader_color,
               (SELECT SUM(quantity) FROM deck_card WHERE deck_id = d.deck_id) as card_count,
               u.username as creator_name
        FROM deck d
        JOIN card c ON d.leader_id = c.card_id
        JOIN user u ON d.creator_id = u.user_id
        WHERE d.creator_id != ?
        ORDER BY d.deck_name
    """, (current_user_id,))
    decks = cursor.fetchall()

    conn.close()
    return render_template('view_decks.html', decks=decks)


@app.route('/add_deck_to_user/<int:deck_id>', methods=['POST'])
def add_deck_to_user(deck_id):
    conn = sqlite3.connect('one_piece_tcg.db')
    cursor = conn.cursor()

    current_user_id = session.get('user_id')

    # Check if user already has this deck
    cursor.execute("""
        SELECT 1 FROM user_deck 
        WHERE user_id = ? AND deck_id = ?
    """, (current_user_id, deck_id))

    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO user_deck (user_id, deck_id)
            VALUES (?, ?)
        """, (current_user_id, deck_id))

    conn.commit()
    conn.close()

    return redirect('/decks')

@app.route('/create_user', methods=['POST'])
def create_user():
    conn = None
    try:
        username = request.form.get('new_username')
        if not username:
            return "Username cannot be empty", 400

        conn = sqlite3.connect('one_piece_tcg.db')
        cursor = conn.cursor()

        # Check if username exists first
        cursor.execute("SELECT user_id FROM user WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return "Username already exists", 400

        cursor.execute("INSERT INTO user (username) VALUES (?)", (username,))
        conn.commit()
        user_id = cursor.lastrowid
        session['user_id'] = user_id
        return redirect('/decks')

    except sqlite3.IntegrityError as e:
        print(f"Database integrity error: {e}")
        return "Username already exists", 400
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "An error occurred", 500
    finally:
        if conn:
            conn.close()

@app.route('/set_user', methods=['POST'])
def set_user():
    user_id = request.form.get('user_id')
    if user_id:
        session['user_id'] = int(user_id)
    return redirect('/decks')


if __name__ == '__main__':
    app.run()
