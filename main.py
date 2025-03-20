from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, flash, session
import requests
import json
import ollama
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'votre_clef_secrete_ici'

API_URL = "https://sandbox-api.sahha.ai/api/v1/profile/biomarker/EFAE25D0-EE36-47E2-902B-512A02AA84DB?startDateTime=2025-02-17T23%3A00%3A00.000Z&endDateTime=2025-03-18T23%3A00%3A00.000Z&types=steps&types=floors_climbed&types=active_hours&types=active_duration&types=activity_low_intensity_duration&types=activity_mid_intensity_duration&types=activity_high_intensity_duration&types=activity_sedentary_duration&types=active_energy_burned&types=total_energy_burned&types=height&types=weight&types=body_mass_index&types=body_fat&types=fat_mass&types=lean_mass&types=waist_circumference&types=resting_energy_burned&types=age&types=biological_sex&types=date_of_birth&types=sleep_start_time&types=sleep_end_time&types=sleep_duration&types=sleep_debt&types=sleep_interruptions&types=sleep_in_bed_duration&types=sleep_awake_duration&types=sleep_light_duration&types=sleep_rem_duration&types=sleep_deep_duration&types=sleep_regularity&types=sleep_latency&types=sleep_efficiency&categories=activity&categories=body&categories=characteristic&categories=sleep"
HEADERS = {
    "Authorization": "account eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwczovL2FwaS5zYWhoYS5haS9jbGFpbXMvYWNjb3VudElkIjoiYzg4NDY0ZTItODU2Ny00MGE0LWE1MmItYjhmNTBlYzAyMTAxIiwiaHR0cHM6Ly9hcGkuc2FoaGEuYWkvY2xhaW1zL2FkbWluIjoiVHJ1ZSIsImh0dHBzOi8vYXBpLnNhaGhhLmFpL2NsYWltcy9hY2NvdW50IjoiVHJ1ZSIsImh0dHBzOi8vYXBpLnNhaGhhLmFpL2NsYWltcy9zYWhoYUFwaVNjb3BlIjoiU2FuZGJveCIsImh0dHBzOi8vYXBpLnNhaGhhLmFpL2NsYWltcy9yZWdpb24iOiJVUyIsImV4cCI6MTc0NDQ2NTc0MiwiaXNzIjoiaHR0cHM6Ly9zYWhoYS1wcm9kdWN0aW9uLmF1LmF1dGgwLmNvbS8iLCJhdWQiOiJodHRwczovL3NhaGhhLXByb2R1Y3Rpb24uYXUuYXV0aDAuY29tL2FwaS92Mi8ifQ.W0UBahoIdN5zb_EBTKvTRcvfCWZ-0k1XerMnvEH01ow"
}

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

def recuperer_donnees_sante():
    try:
        reponse = requests.get(API_URL, headers=HEADERS)
        
        if reponse.status_code == 200:
            donnees = reponse.json()
            
            if isinstance(donnees, dict) and 'resume' in donnees:
                return donnees
            
            resume = {
                "pas": sum(float(entree.get('value', 0)) for entree in donnees if entree.get('type') == 'steps'),
                "duree_activite": sum(float(entree.get('value', 0)) for entree in donnees if entree.get('type') == 'active_duration'),
                "energie_burnee": sum(float(entree.get('value', 0)) for entree in donnees if entree.get('type') == 'active_energy_burned'),
                "duree_sommeil": sum(float(entree.get('value', 0)) for entree in donnees if entree.get('type') == 'sleep_duration'),
                "etages_gravis": sum(float(entree.get('value', 0)) for entree in donnees if entree.get('type') == 'floors_climbed')
            }
            
            with open("donnees_sante.json", "w") as f:
                json.dump({"donnees_brutes": donnees, "resume": resume}, f, indent=4)
            
            return {"donnees_brutes": donnees, "resume": resume}
        else:
            print(f"Erreur API: {reponse.status_code}")
            return None
    except Exception as e:
        print(f"Erreur: {e}")
        return None

def poser_question_ollama(question):
    try:
        donnees = recuperer_donnees_sante()
        if not donnees:
            return "Je ne peux pas accéder aux données de santé pour le moment."
        resume = donnees["resume"]
        donnees_formatees = f"Données: pas={resume['pas']}, activité={resume['duree_activite']}min, sommeil={resume['duree_sommeil']}min"
        
        prompt = f"Tu es un coach sportif concis. Données: {donnees_formatees}. Question: {question}. Réponds en 4 phrases maximum."
        
        reponse = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un coach sportif qui donne des conseils brefs et précis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.7,
                "top_k": 40,
                "top_p": 0.9,
                "num_ctx": 512
            }
        )
        
        if reponse and 'message' in reponse and 'content' in reponse['message']:
            return reponse['message']['content']
        return "Désolé, je n'ai pas pu générer une réponse appropriée."
    except Exception as e:
        print(f"Erreur lors de la génération de la réponse: {e}")
        return "Désolé, une erreur s'est produite lors de la génération de la réponse."

def generer_recommandations():
    try:
        print("Début de la génération des recommandations")
        donnees = recuperer_donnees_sante()
        if not donnees:
            print("Erreur: Impossible de récupérer les données de santé")
            return {'error': 'Impossible de récupérer les données de santé'}
        
        resume = donnees["resume"]
        print(f"Données récupérées: {resume}")
        
        prompt = f"""Tu es un coach sportif qui donne des conseils précis. Génère exactement 3 recommandations basées sur ces données:
- Pas: {resume['pas']} pas
- Activité: {resume['duree_activite']} minutes
- Sommeil: {resume['duree_sommeil']} minutes

IMPORTANT: Réponds EXACTEMENT dans ce format (commence chaque ligne par le mot-clé suivi de deux points):
Activité: [ta recommandation pour l'activité physique]
Sommeil: [ta recommandation pour le sommeil]
Nutrition: [ta recommandation pour l'alimentation]"""

        print("Envoi de la requête à Ollama")
        reponse = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un coach sportif qui donne des conseils brefs et précis. Tu DOIS suivre EXACTEMENT le format demandé."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.7,
                "top_k": 40,
                "top_p": 0.9,
                "num_ctx": 512
            }
        )

        if not reponse or 'message' not in reponse or 'content' not in reponse['message']:
            print("Erreur: Réponse invalide de Ollama")
            return {'error': 'Erreur lors de la génération des recommandations'}

        texte = reponse['message']['content']
        print(f"Réponse reçue: {texte}")
        
        recommandations = {}
        
        lignes = [l.strip() for l in texte.split('\n') if l.strip()]
        for ligne in lignes:
            if ':' not in ligne:
                continue
            
            categorie, contenu = [part.strip() for part in ligne.split(':', 1)]
            categorie = categorie.lower()
            
            if categorie in ['activité', 'activite']:
                recommandations['activite'] = contenu
            elif categorie in ['sommeil']:
                recommandations['sommeil'] = contenu
            elif categorie in ['nutrition']:
                recommandations['nutrition'] = contenu

        print(f"Recommandations extraites: {recommandations}")

        categories_requises = ['activite', 'sommeil', 'nutrition']
        for categorie in categories_requises:
            if categorie not in recommandations:
                recommandations[categorie] = "Pas de recommandation disponible pour cette catégorie."

        print(f"Recommandations finales: {recommandations}")
        return recommandations

    except Exception as e:
        print(f"Erreur lors de la génération des recommandations: {e}")
        return {'error': 'Une erreur est survenue lors de la génération des recommandations'}

@app.route('/')
def index():
    donnees = recuperer_donnees_sante()
    if donnees and 'resume' in donnees:
        health_data = {
            'activite': f"{donnees['resume']['duree_activite']:.0f} min",
            'sommeil': f"{donnees['resume']['duree_sommeil'] / 60:.1f} h",
            'pas': f"{int(donnees['resume']['pas'])} pas"
        }
    else:
        health_data = {
            'activite': 'N/A',
            'sommeil': 'N/A',
            'pas': 'N/A'
        }
    return render_template('index.html', health_data=health_data)

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
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    if request.method == 'POST':
        updates = []
        values = []
        fields = ['name', 'age', 'weight', 'height', 'objective', 'sahha_url', 'sahha_token']
        for field in fields:
            if field in request.form and request.form[field]:
                updates.append(f'{field} = ?')
                values.append(request.form[field])
        if updates:
            update_query = f"UPDATE users SET {' ,'.join(updates)} WHERE id = ?"
            values.append(session['user_id'])
            conn = get_db()
            conn.execute(update_query, values)
            conn.commit()
            conn.close()
            flash('Profil mis à jour avec succès!', 'success')
    return render_template('account.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('index'))

@app.route('/recommendations')
def recommendations():
    return render_template('recommendations.html')

@app.route('/recommendations/data')
def recommendations_data():
    try:
        recommandations = generer_recommandations()
        print(f"Route /recommendations/data - Recommandations générées: {recommandations}")
        return jsonify(recommandations)
    except Exception as e:
        print(f"Route /recommendations/data - Erreur: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/recommendations_data')
def recommendations_data_old():
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorisé'}), 401
    recommandations = generer_recommandations()
    return jsonify(recommandations)

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
        with open('donnees_sante.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier JSON: {e}")
        return jsonify({})

@app.route('/public/<path:fichier>')
def fichiers_statiques(fichier):
    return send_from_directory("public", fichier)

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour accéder au chatbot', 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        message_utilisateur = request.json.get("message", "")
        print(f"Message utilisateur: {message_utilisateur}")
        reponse = poser_question_ollama(message_utilisateur)
        return jsonify({"text": reponse.strip()})
    return render_template('chatbot.html')

@app.route('/accueil')
def accueil():
    return send_from_directory("public", "index.html")

@app.route('/poser_question', methods=['POST'])
def poser_question():
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({'error': 'Question manquante'}), 400
            
        question = data['question']
        reponse = poser_question_ollama(question)
        return jsonify({'reponse': reponse})
    except Exception as e:
        print(f"Erreur lors du traitement de la question: {e}")
        return jsonify({'error': 'Une erreur est survenue'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)