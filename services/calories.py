def ajuster_besoins_caloriques(besoins, objectif, activite):
    if objectif == "perte de poids":
        besoins -= 300
    elif objectif == "gain de muscle":
        besoins += 500 
    if activite == "faible":
        besoins -= 200
    elif activite == "moderee":
        pass 
    elif activite == "eleve":
        besoins += 300 

    return besoins