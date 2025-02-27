import random

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

def generer_seance(obj):
    return random.choice(seances.get(obj, ["Marche 30 min"]))
