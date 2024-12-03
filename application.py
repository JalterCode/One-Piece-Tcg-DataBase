from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


@app.route('/')
def index():
    conn = sqlite3.connect('one_piece_tcg.db')
    cursor = conn.cursor()

    cursor.execute("gitSELECT * FROM card")
    cards = cursor.fetchall()

    conn.close()

    return render_template('index.html', cards=cards)


if __name__ == '__main__':
    app.run()
