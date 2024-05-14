from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


@app.route('/')
def Menu():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users')
    menu = cur.fetchall()
    return render_template('menu.html', menu=menu)
