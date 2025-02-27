from flask import Flask, request, jsonify

app = Flask(__name__)
@app.route('/')
def home():
    return "Bienvenue sur votre espace santé !"
@app.route('/data', methods=['POST'])
def collect_data():
    data = request.json
    return jsonify({"message": "Données reçues et traitées !"}), 200

if __name__ == '__main__':
    app.run(debug=True)