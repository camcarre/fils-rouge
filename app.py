from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
import sqlite3
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'votre_clef_secrete_ici'

def get_db():
    conn = sqlite3.connect('user_data.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            weight FLOAT,
            height INTEGER,
            objective TEXT,
            sahha_url TEXT,
            sahha_token TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            flash('Connexion réussie!', 'success')
            return redirect(url_for('account'))
        else:
            flash('Email ou mot de passe incorrect', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        sahha_url = request.form['sahha_url']
        sahha_token = request.form['sahha_token']
        
        password_hash = generate_password_hash(password)
        
        conn = get_db()
        try:
            conn.execute('INSERT INTO users (email, password_hash, name, sahha_url, sahha_token) VALUES (?, ?, ?, ?, ?)',
                       (email, password_hash, name, sahha_url, sahha_token))
            conn.commit()
            flash('Compte créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Cet email est déjà utilisé', 'error')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour accéder à votre profil', 'error')
        return redirect(url_for('login'))
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', 
                       (session['user_id'],)).fetchone()
    
    if request.method == 'POST':
        # Mise à jour du profil
        updates = []
        values = []
        fields = ['name', 'age', 'weight', 'height', 'objective', 'sahha_url', 'sahha_token']
        
        for field in fields:
            if field in request.form and request.form[field]:
                updates.append(f'{field} = ?')
                values.append(request.form[field])
        
        if updates:
            values.append(session['user_id'])
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            conn.execute(query, values)
            conn.commit()
            flash('Profil mis à jour avec succès!', 'success')
            return redirect(url_for('account'))
    
    conn.close()
    return render_template('account.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('index'))

@app.route('/recommendations')
def recommendations():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour voir vos recommandations', 'error')
        return redirect(url_for('login'))
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', 
                       (session['user_id'],)).fetchone()
    conn.close()

    mock_data = {
        'sleep_quality': 'Bonne qualité de sommeil',
        'sleep_duration': '8 heures par nuit',
        'sleep_tips': 'Maintenez un horaire de sommeil régulier',
        'meal_plan': 'Plan équilibré avec protéines et légumes',
        'calories': '2000 kcal par jour',
        'nutrition_tips': 'Privilégiez les aliments complets',
        'training_program': 'Programme de force 3x par semaine',
        'training_intensity': 'Modérée à élevée',
        'exercise_tips': 'Échauffez-vous avant chaque séance'
    }
    return render_template('recommendations.html', **mock_data)

@app.route('/user_data')
def user_data():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    if user:
        user_data = {
            'id': user['id'],
            'email': user['email'],
            'name': user['name'],
            'age': user['age'],
            'weight': user['weight'],
            'height': user['height'],
            'objective': user['objective'],
            'sahha_url': user['sahha_url'],
            'sahha_token': user['sahha_token']
        }
        return jsonify(user_data)
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/get_json_data')
def get_json_data():
    try:
        with open('data.json', 'r') as file:
            data = json.load(file)
            return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "Data file not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON data"}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
