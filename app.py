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
