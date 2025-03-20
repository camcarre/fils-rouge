

## ⚙️ **Installation (facile, promis 🤞)**  

### 📌 **Ce qu’il te faut**  

Avant de commencer, assure-toi d’avoir :  
✔️ **Python 3.8+** installé (prends la dernière version dispo, c’est toujours mieux)  
✔️ **Ollama** (le moteur qui va faire tourner l’IA)  

### 🔽 **Installer Ollama**  

1. Télécharge et installe **Ollama** depuis leur site :  
   👉 [https://ollama.ai/download](https://ollama.ai/download)  

2. Lance Ollama avec cette commande (ça démarre le serveur) :  

   ```bash
   ollama serve
   ```

---

## 🏗️ **Mise en place du projet**  

### 🔹 **1. Clone le repo et installe les dépendances**  

Si ce n’est pas déjà fait, clone le projet et rentre dedans :  

```bash
git clone https://github.com/camcarre/fils-rouge.git

```

Active un environnement virtuel pour éviter d’installer des paquets n’importe où :  

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# ou pour Windows :
venv\Scripts\activate
```

Installe les dépendances :  

```bash
pip install -r requirements.txt
```

### 🔹 **2. Configurer les paramètres**  

Copie le fichier de config et ajuste-le si besoin :  

```bash
cp config.py.example config.py
```

Tu peux modifier **config.py** pour changer le modèle utilisé.  

### 🔹 **3. Changer de modèle IA (si tu veux)**  

Si tu veux tester un autre modèle, fais comme ça :  

1. Stoppe Ollama :  

   ```bash
   ollama stop
   ```

2. Télécharge un modèle (exemple avec **Mistral**) :  

   ```bash
   ollama pull mistral:latest
   ```

3. Mets à jour ton fichier **config.py** :  

   ```python
   IA_MODEL = "mistral:latest"
   ```

4. Redémarre Ollama :  

   ```bash
   ollama serve
   ```

---

## 🚀 **Lancer l’application**  

1. Assure-toi qu’Ollama tourne bien en arrière-plan :  

   ```bash
   ollama serve
   ```

2. Démarre le chatbot :  

   ```bash
   python main.py
   ```

3. Ouvre ton navigateur et va sur **[http://127.0.0.1:5000](http://127.0.0.1:5000)**  

---

## 🔍 **Voir les modèles disponibles**  

Tu peux voir quels modèles sont installés sur ta machine avec :  

```bash
ollama list
```

Si tu veux tester un autre modèle :  

```bash
ollama pull nom_du_modele
```
La liste complète est dispo ici : **[https://ollama.ai/models](https://ollama.ai/models)**  

---

## 🛠️ **Besoin d’aide ?**  

Si t’as un souci ou une question, check d’abord la doc officielle d’Ollama :  
👉 [https://ollama.ai/docs](https://ollama.ai/docs)  
