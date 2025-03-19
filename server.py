from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import requests
import json
import ollama
from datetime import datetime

app = Flask(__name__)

API_URL = "https://sandbox-api.sahha.ai/api/v1/profile/biomarker/EFAE25D0-EE36-47E2-902B-512A02AA84DB?startDateTime=2025-02-17T23%3A00%3A00.000Z&endDateTime=2025-03-18T23%3A00%3A00.000Z&types=steps&types=floors_climbed&types=active_hours&types=active_duration&types=activity_low_intensity_duration&types=activity_mid_intensity_duration&types=activity_high_intensity_duration&types=activity_sedentary_duration&types=active_energy_burned&types=total_energy_burned&types=height&types=weight&types=body_mass_index&types=body_fat&types=fat_mass&types=lean_mass&types=waist_circumference&types=resting_energy_burned&types=age&types=biological_sex&types=date_of_birth&types=sleep_start_time&types=sleep_end_time&types=sleep_duration&types=sleep_debt&types=sleep_interruptions&types=sleep_in_bed_duration&types=sleep_awake_duration&types=sleep_light_duration&types=sleep_rem_duration&types=sleep_deep_duration&types=sleep_regularity&types=sleep_latency&types=sleep_efficiency&categories=activity&categories=body&categories=characteristic&categories=sleep"
HEADERS = {
    "Authorization": "account eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwczovL2FwaS5zYWhoYS5haS9jbGFpbXMvYWNjb3VudElkIjoiYzg4NDY0ZTItODU2Ny00MGE0LWE1MmItYjhmNTBlYzAyMTAxIiwiaHR0cHM6Ly9hcGkuc2FoaGEuYWkvY2xhaW1zL2FkbWluIjoiVHJ1ZSIsImh0dHBzOi8vYXBpLnNhaGhhLmFpL2NsYWltcy9hY2NvdW50IjoiVHJ1ZSIsImh0dHBzOi8vYXBpLnNhaGhhLmFpL2NsYWltcy9zYWhoYUFwaVNjb3BlIjoiU2FuZGJveCIsImh0dHBzOi8vYXBpLnNhaGhhLmFpL2NsYWltcy9yZWdpb24iOiJVUyIsImV4cCI6MTc0NDQ2NTc0MiwiaXNzIjoiaHR0cHM6Ly9zYWhoYS1wcm9kdWN0aW9uLmF1LmF1dGgwLmNvbS8iLCJhdWQiOiJodHRwczovL3NhaGhhLXByb2R1Y3Rpb24uYXUuYXV0aDAuY29tL2FwaS92Mi8ifQ.W0UBahoIdN5zb_EBTKvTRcvfCWZ-0k1XerMnvEH01ow"
}

def recuperer_donnees_sante():
    try:
        reponse = requests.get(API_URL, headers=HEADERS)
        if reponse.status_code == 200:
            donnees = reponse.json()
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
        donnees_formatees = (
            "Voici vos données de santé sur la période:\n"
            f"- Pas: {resume['pas']} pas\n"
            f"- Activité: {resume['duree_activite']:.1f} minutes\n"
            f"- Énergie brûlée: {resume['energie_burnee']:.1f} kcal\n"
            f"- Sommeil: {resume['duree_sommeil']:.1f} minutes\n"
            f"- Étages gravis: {resume['etages_gravis']:.1f}"
        )
        prompt = (
            f"{donnees_formatees}\n\n"
            f"Question: {question}\n\n"
            "Analyse ces données et donne des conseils pratiques et personnalisés."
        )
        reponse = ollama.chat(
            model="mistral",
            messages=[
                {"role": "system", "content": "Tu es un assistant santé. Donne des conseils pratiques basés sur les données réelles."},
                {"role": "user", "content": prompt}
            ]
        )
        return reponse['message']['content']
    except Exception as e:
        print(f"Erreur Ollama: {e}")
        return f"Désolé, une erreur est survenue: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommendations')
def recommendations():
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

@app.route('/account', methods=['GET'])
def account():
    mock_user = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'age': 30,
        'weight': 75,
        'height': 175,
        'objective': 'maintenance'
    }
    return render_template('account.html', user=mock_user)

@app.route('/update_account', methods=['POST'])
def update_account():
    flash('Profil mis à jour avec succès!', 'success')
    return redirect(url_for('account'))

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/chatbot', methods=['POST'])
def chatbot_post():
    message_utilisateur = request.json.get("message", "")
    print(f"Message utilisateur: {message_utilisateur}")
    reponse = poser_question_ollama(message_utilisateur)
    return jsonify({"text": reponse.strip()})

if __name__ == '__main__':
    app.run(debug=True)