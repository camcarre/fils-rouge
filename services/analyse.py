def calcul_bmr(sexe, poids, taille, age):
    if sexe == "homme":
        return 88.36 + (13.4 * poids) + (4.8 * taille) - (5.7 * age)
    else:
        return 447.6 + (9.2 * poids) + (3.1 * taille) - (4.3 * age)

def besoins_caloriques(bmr, activite):
    facteurs = {
        "sédentaire": 1.2,
        "faible": 1.375,
        "modérée": 1.55,
        "élevée": 1.725,
        "intense": 1.9
    }
    return bmr * facteurs.get(activite, 1.55)