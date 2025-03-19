from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
