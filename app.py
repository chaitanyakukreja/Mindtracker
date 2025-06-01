from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a strong key in production

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            username TEXT,
            date TEXT,
            mood TEXT,
            reason TEXT,
            habits TEXT,
            intention TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------- HELPER FUNCTIONS ----------
def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def validate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None

def save_entry(username, form_data):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO entries (username, date, mood, reason, habits, intention)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        username,
        datetime.now().strftime('%Y-%m-%d'),
        form_data.get('mood'),
        form_data.get('reason'),
        form_data.get('habits'),
        form_data.get('intention')
    ))
    conn.commit()
    conn.close()

def get_entries_for_user(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT date, mood, reason, habits, intention FROM entries WHERE username=? ORDER BY date DESC", (username,))
    entries = c.fetchall()
    conn.close()
    return entries

def get_weekly_summary(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT mood, habits FROM entries
        WHERE username=? AND date >= date('now', '-7 day')
    ''', (username,))
    data = c.fetchall()
    conn.close()

    mood_stats = {}
    habit_stats = {}

    for mood, habits in data:
        mood_stats[mood] = mood_stats.get(mood, 0) + 1
        for habit in habits.split(','):
            habit = habit.strip()
            if habit:
                habit_stats[habit] = habit_stats.get(habit, 0) + 1

    return mood_stats, habit_stats

# ---------- ROUTES ----------
@app.route('/')
def home():
    return render_template('main.html', page="home")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if add_user(request.form['username'], request.form['password']):
            return redirect(url_for('login'))
        else:
            return "User already exists!"
    return render_template('main.html', page="register")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if validate_user(request.form['username'], request.form['password']):
            session['username'] = request.form['username']
            return redirect(url_for('dashboard'))
        else:
            return "Invalid login!"
    return render_template('main.html', page="login")

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        save_entry(session['username'], request.form)
        return redirect(url_for('dashboard'))
    entries = get_entries_for_user(session['username'])
    return render_template('main.html', page="dashboard", username=session['username'], entries=entries)

@app.route('/summary')
def summary():
    if 'username' not in session:
        return redirect(url_for('login'))
    mood_stats, habit_stats = get_weekly_summary(session['username'])
    return render_template('main.html', page="summary", username=session['username'],
                           mood_stats=mood_stats, habit_stats=habit_stats)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

# ---------- RUN LOCALLY ----------
if __name__ == '__main__':
    app.run(debug=True)
