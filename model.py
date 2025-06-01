import sqlite3
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY, username TEXT, date TEXT,
        mood TEXT, reason TEXT, intention TEXT,
        habits TEXT, q1 TEXT, q2 TEXT, q3 TEXT)''')
    conn.commit()
    conn.close()

def add_user(username, password):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def validate_user(username, password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return bool(result)

def save_entry(username, form):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""INSERT INTO entries (username, date, mood, reason, intention, habits, q1, q2, q3)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (username, datetime.now().strftime("%Y-%m-%d"),
               form['mood'], form['reason'], form['intention'],
               form['habits'], form['q1'], form['q2'], form['q3']))
    conn.commit()
    conn.close()

def get_entries_for_user(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT date, mood, intention FROM entries WHERE username=? ORDER BY date DESC LIMIT 7", (username,))
    entries = c.fetchall()
    conn.close()
    return entries

def get_weekly_summary(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    c.execute("SELECT mood, habits FROM entries WHERE username=? AND date >= ?", (username, last_week))
    rows = c.fetchall()
    conn.close()

    mood_count = {}
    habit_count = {}
    for mood, habits in rows:
        mood_count[mood] = mood_count.get(mood, 0) + 1
        for habit in habits.split(','):
            habit = habit.strip()
            if habit:
                habit_count[habit] = habit_count.get(habit, 0) + 1
    return mood_count, habit_count
