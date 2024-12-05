from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect('one_piece_tcg.db')
    cursor = conn.cursor()

    selected_color = None
    selected_cost = None
    selected_set = None
    if request.method == 'POST':
        selected_color = request.form.get('color')
        selected_cost = request.form.get('cost')
        selected_set = request.form.get('set')
        query = 'SELECT * FROM Card WHERE 1=1'
        params = []
        if selected_color:
            query += ' AND Colour = ?'
            params.append(selected_color)
        if selected_cost:
            query += ' AND Cost = ?'
            params.append(selected_cost)
        if selected_set:
            query += ' And set_id = ?'
            params.append(selected_set)
        cursor.execute(query, params)
    else:
        cursor.execute('SELECT * FROM Card')

    cards = cursor.fetchall()
    conn.close()

    return render_template('index.html', cards=cards, selected_color=selected_color, selected_cost=selected_cost, selected_set=selected_set)

if __name__ == '__main__':
    app.run()
