from flask import Flask, request, render_template, jsonify, redirect
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
from services.analyse import calcul_bmr, besoins_caloriques
from services.calories import ajuster_besoins_caloriques
from services.menu import generer_menu
from services.seance import generer_seance
import sqlite3

app = Flask(__name__)

# user_data = pd.read_csv('data/user_data.csv')

X = pd.DataFrame({
    'age': [25, 30, 22, 28, 35],
    'sexe': [0, 1, 0, 0, 1], 
    'poids': [70, 60, 80, 75, 65],
    'taille': [175, 160, 180, 170, 165],
    'objectif': [0, 1, 0, 1, 0], 
    'activite': [1, 2, 1, 3, 2],  
    'recommandation_menu': [1, 2, 1, 2, 1],
    'recommandation_seance': [1, 2, 1, 2, 1]
})

y_menu = X['recommandation_menu']
y_seance = X['recommandation_seance']

X = X.drop(columns=['recommandation_menu', 'recommandation_seance'])

X = pd.get_dummies(X, columns=['sexe', 'activite', 'objectif'])

dummy_columns = X.columns

X_train, X_test, y_train_menu, y_test_menu = train_test_split(X, y_menu, test_size=0.2, random_state=42)
X_train, X_test, y_train_seance, y_test_seance = train_test_split(X, y_seance, test_size=0.2, random_state=42)

menu_model = RandomForestClassifier(n_estimators=100, random_state=42)
menu_model.fit(X_train, y_train_menu)

seance_model = RandomForestClassifier(n_estimators=100, random_state=42)
seance_model.fit(X_train, y_train_seance)

data = {
    "age": [25, 30, 22, 28, 35],
    "sexe": [0, 1, 0, 0, 1], 
    "poids": [70, 60, 80, 75, 65],
    "taille": [175, 160, 180, 170, 165],
    "objectif": [0, 1, 0, 1, 0], 
    "activite": [1, 2, 1, 3, 2],  
    "entraineur_recommande": [1, 0.9, 0.8, 0.85, 0.9]  
}

df = pd.DataFrame(data)

X = df.drop(columns=["entraineur_recommande"]) 
y = df["entraineur_recommande"]

model = RandomForestRegressor(n_estimators=100, random_state=42)

model.fit(X, y)


def generer_menu(besoins_caloriques, utilisateur_data):
    utilisateur_data = pd.get_dummies(utilisateur_data, columns=['sexe', 'activite', 'objectif'])
    utilisateur_data = utilisateur_data.reindex(columns=dummy_columns, fill_value=0)
    prediction = menu_model.predict(utilisateur_data)
    return prediction[0]


def generer_seance(objectif, utilisateur_data):
    utilisateur_data = pd.get_dummies(utilisateur_data, columns=['sexe', 'activite', 'objectif'])
    utilisateur_data = utilisateur_data.reindex(columns=dummy_columns, fill_value=0)
    prediction = seance_model.predict(utilisateur_data)
    return prediction[0]


def generer_conseils(user_id):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user_data = c.fetchone()
    conn.close()

    if user_data:
        return {
            'name': user_data[1],
            'email': user_data[2],
            'created_at': user_data[3]
        }
    else:
        return None


def calculer_proposition_sommeil(sommeil_dernieres_semaines):
    print(f"Sleep data for last weeks: {sommeil_dernieres_semaines}")  # Debugging statement
    moyenne_sommeil = sum(sommeil_dernieres_semaines) / len(sommeil_dernieres_semaines)
    if moyenne_sommeil < 7:
        recommandation = "Essayez d'augmenter votre sommeil à au moins 7 heures par nuit."
    else:
        recommandation = "Continuez à maintenir un bon rythme de sommeil."
    print(f"Sleep recommendation: {recommandation}")  # Debugging statement
    return recommandation


@app.route('/')
def home():
    return redirect('/recommandation')

@app.route('/recommandation')
def afficher_recommandations():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT sexe, poids, taille, objectif, activite FROM users ORDER BY created_at DESC LIMIT 1')
    dernier_utilisateur = c.fetchone()
    conn.close()

    if dernier_utilisateur:
        user_id = dernier_utilisateur[0]
        user_data = pd.DataFrame([{
            'sexe': dernier_utilisateur[0],
            'poids': dernier_utilisateur[1],
            'taille': dernier_utilisateur[2],
            'objectif': dernier_utilisateur[3],
            'activite': dernier_utilisateur[4]
        }])

        bmr = calcul_bmr(user_data['sexe'][0], user_data['poids'][0], user_data['taille'][0], 25)
        besoins = besoins_caloriques(bmr, user_data['activite'][0])
        besoins_ajustes = ajuster_besoins_caloriques(besoins, user_data['objectif'][0], user_data['activite'][0])

        repas = generer_menu(besoins_ajustes, user_data)
        seance = generer_seance(user_data['objectif'][0], user_data)

        return render_template('resultat.html',
                             besoins_caloriques=round(besoins_ajustes, 2),
                             menu=repas,
                             seance=seance,
                             proposition_sommeil="Votre recommandation de sommeil")
    else:
        return "Aucun utilisateur trouvé dans la base de données."


@app.route('/recommandation', methods=['POST'])
def recommander():
    if request.is_json: 
        data = request.get_json() 

        sommeil_dernieres_semaines = data.get("sommeil_dernieres_semaines", [])
        
        proposition_sommeil = calculer_proposition_sommeil(sommeil_dernieres_semaines)
        
        bmr = calcul_bmr(data["sexe"], data["poids"], data["taille"], data["age"])
        besoins = besoins_caloriques(bmr, data["activite"])
        besoins_ajustes = ajuster_besoins_caloriques(besoins, data["objectif"], data["activite"])

        utilisateur_data = pd.DataFrame([data])
        repas = generer_menu(besoins_ajustes, utilisateur_data)
        seance = generer_seance(data["objectif"], utilisateur_data)

        return jsonify({
            "besoins_caloriques": round(besoins_ajustes, 2),
            "menu": repas,
            "seance": seance,
            "proposition_sommeil": proposition_sommeil
        })

    else:
        age = int(request.form['age'])
        sexe = 1 if request.form['sexe'] == 'femme' else 0
        poids = float(request.form['poids'])
        taille = int(request.form['taille'])
        objectif = 'gain musculaire' if request.form['objectif'] == 'gain musculaire' else 'perte de poids'
        activite = request.form['activite']
        
        activite_dict = {'faible': 1, 'moderee': 2, 'eleve': 3}
        activite_num = activite_dict.get(activite, 1) 

        utilisateur_data = np.array([[age, sexe, poids, taille, 1 if objectif == 'gain musculaire' else 0, activite_num]])
        
        prediction = model.predict(utilisateur_data)

        besoins_caloriques = round(poids * 24 * 1.2, 2)

        sommeil_jours = [
            float(request.form['sommeil_jour_1']),
            float(request.form['sommeil_jour_2']),
            float(request.form['sommeil_jour_3']),
            float(request.form['sommeil_jour_4']),
            float(request.form['sommeil_jour_5'])
        ]

        proposition_sommeil = calculer_proposition_sommeil(sommeil_jours)

        seances_passees = request.form['seances_passees'].split(',')
        
        if len(seances_passees) > 3:
            besoins_caloriques *= 1.1
            proposition_sommeil = "Augmentez votre sommeil pour récupérer de vos séances intenses."
        
        utilisateur_data = pd.DataFrame([{'age': age, 'sexe': sexe, 'poids': poids, 'taille': taille, 'activite': activite_num, 'objectif': 1 if objectif == 'gain musculaire' else 0}])
        repas = generer_menu(besoins_caloriques, utilisateur_data)
        seance = generer_seance(objectif, utilisateur_data)

        return render_template('resultat.html', 
                               besoins_caloriques=besoins_caloriques, 
                               entrainement_recommande=round(prediction[0], 2),
                               menu=repas,
                               seance=seance,
                               proposition_sommeil=proposition_sommeil,
                               message="Votre entraînement est recommandé à " + str(round(prediction[0] * 100, 2)) + "% d'efficacité")

if __name__ == '__main__':
    app.run(debug=True)