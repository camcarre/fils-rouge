from flask import Flask, request, render_template, jsonify
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd
from services.calories import ajuster_besoins_caloriques

app = Flask(__name__)

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

model = LinearRegression()

model.fit(X, y)

def calcul_bmr(sexe, poids, taille, age):
    if sexe == 0:
        return 66.5 + (13.75 * poids) + (5.003 * taille) - (6.75 * age)
    else: 
        return 655 + (9.563 * poids) + (1.850 * taille) - (4.676 * age)

def besoins_caloriques(bmr, activite):
    if activite == "faible":
        return bmr * 1.2 
    elif activite == "moderee":
        return bmr * 1.55 
    elif activite == "eleve":
        return bmr * 1.9 
    else:
        return bmr 


def generer_menu(besoins_caloriques):
    return f"Menu avec {besoins_caloriques} calories : 3 repas équilibrés."

def generer_seance(objectif, activite):
    if objectif == "perte de poids":
        return f"Entraînement cardio de {activite} intensité pour la perte de poids."
    else:
        return f"Entraînement de renforcement musculaire pour le gain musculaire."

@app.route('/')
def home():
    return render_template('formulaire.html') 

@app.route('/recommandation', methods=['POST'])
def recommander():
    if request.is_json: 
        data = request.get_json() 

        bmr = calcul_bmr(data["sexe"], data["poids"], data["taille"], data["age"])
        besoins = besoins_caloriques(bmr, data["activite"])
        besoins_ajustes = ajuster_besoins_caloriques(besoins, data["objectif"], data["activite"])

        repas = generer_menu(besoins_ajustes)
        seance = generer_seance(data["objectif"], data["activite"])

        return jsonify({
            "besoins_caloriques": round(besoins_ajustes, 2),
            "menu": repas,
            "seance": seance
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

        return render_template('resultat.html', 
                               besoins_caloriques=besoins_caloriques, 
                               entrainement_recommande=round(prediction[0], 2),
                               message="Votre entraînement est recommandé à " + str(round(prediction[0] * 100, 2)) + "% d'efficacité")

if __name__ == '__main__':
    app.run(debug=True)