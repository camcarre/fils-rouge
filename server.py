from flask import Flask, request, render_template
from services.analyse import calcul_bmr, besoins_caloriques
from services.menu import generer_menu
from services.seance import generer_seance

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('formulaire.html') 

@app.route('/recommandation', methods=['POST'])
def recommander():
    """ Gère les recommandations personnalisées """
    data = request.form 
    bmr = calcul_bmr(data["sexe"], float(data["poids"]), float(data["taille"]), int(data["age"]))
    besoins = besoins_caloriques(bmr, data["activite"])
    repas = generer_menu(besoins)
    seance = generer_seance(data["objectif"])

    return f"""
    <html>
        <head><title>Recommandations</title></head>
        <body>
            <h1>Recommandations personnalisées</h1>
            <p><strong>Besoins caloriques :</strong> {round(besoins, 2)} calories par jour</p>
            <h2>Menu proposé :</h2>
            <ul>
                <li><strong>Petit-déjeuner :</strong> {repas['petit-déjeuner']}</li>
                <li><strong>Déjeuner :</strong> {repas['déjeuner']}</li>
                <li><strong>Dîner :</strong> {repas['dîner']}</li>
            </ul>
            <h2>Séance proposée :</h2>
            <p>{seance}</p>
        </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True)