import random
import pandas as pd

seances = {
    "perte de poids": [
        "Course à pied 30 min",
        "HIIT 20 min",
        "Natation 45 min"
    ],
    "prise de muscle": [
        "Musculation haut du corps",
        "Squats et fentes",
        "Pompes et tractions"
    ],
    "équilibre et bien-être": [
        "Yoga 45 min",
        "Pilates 30 min",
        "Marche rapide 1h"
    ]
}

def generer_seance(objectif, utilisateur_data):
    print(f"Generating session for objective: {objectif}") 
    print(f"User data for prediction: {utilisateur_data}")
    utilisateur_data = pd.get_dummies(utilisateur_data, columns=['sexe', 'activite', 'objectif'])
    utilisateur_data = utilisateur_data.reindex(columns=dummy_columns, fill_value=0)
    prediction = seance_model.predict(utilisateur_data)
    print(f"Session prediction: {prediction[0]}")
    return prediction[0]
