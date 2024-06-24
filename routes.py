from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


@app.route('/')
def Menu():
    conn = sqlite3.connect('Genshin Impact Builds Website.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM teams')
    menu = cur.fetchall()
    return render_template('menu.html', menu=menu)


@app.route('/teams')
def Teams():
    conn = sqlite3.connect('Genshin Impact Builds Website.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM teams')
    teams = cur.fetchall()
    return render_template('teams.html', teams=teams)


@app.route('/teams/<int:id>')
def Team(id):
    conn = sqlite3.connect('Genshin Impact Builds Website.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM teams WHERE id = ?', (id,))
    team = cur.fetchone()
    return render_template('team.html', team=team)


if __name__ == "__main__":
    app.run(debug=True)
