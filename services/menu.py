import random

menu = {
    "petit-déjeuner": [
        {"nom": "Omelette et pain complet", "calories": 350},
        {"nom": "Yaourt, granola et miel", "calories": 300},
        {"nom": "Smoothie banane protéiné", "calories": 400}
    ],
    "déjeuner": [
        {"nom": "Poulet-riz-légumes", "calories": 600},
        {"nom": "Salade quinoa avocat", "calories": 500},
        {"nom": "Pâtes complètes saumon", "calories": 700}
    ],
    "dîner": [
        {"nom": "Soupe de légumes et fromage", "calories": 400},
        {"nom": "Tofu sauté légumes", "calories": 450},
        {"nom": "Omelette aux champignons", "calories": 350}
    ]
}

def generer_menu(besoins):
    repas = {}
    for type_repas, options in menu.items():
        options_valides = [o for o in options if o['calories'] <= besoins / 3]
        if options_valides:
            choix = random.choice(options_valides)
            repas[type_repas] = choix["nom"]
    return repas