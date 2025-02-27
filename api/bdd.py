import requests
import sqlite3
import sys

url = "https://sandbox-api.sahha.ai/api/v1/profile/score/WAJDbLDMeZWbT3AAYEJOE49Ijlg2?startDateTime=2025-02-21T00%3A00%3A00.000Z&endDateTime=2025-02-27T12%3A48%3A31.199Z&types=activity&types=sleep&types=readiness"
headers = {
    "Authorization": "account eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwczovL2FwaS5zYWhoYS5haS9jbGFpbXMvYWNjb3VudElkIjoiYzg4NDY0ZTItODU2Ny00MGE0LWE1MmItYjhmNTBlYzAyMTAxIiwiaHR0cHM6Ly9hcGkuc2FoaGEuYWkvY2xhaW1zL2FkbWluIjoiVHJ1ZSIsImh0dHBzOi8vYXBpLnNhaGhhLmFpL2NsYWltcy9hY2NvdW50IjoiVHJ1ZSIsImh0dHBzOi8vYXBpLnNhaGhhLmFpL2NsYWltcy9zYWhoYUFwaVNjb3BlIjoiU2FuZGJveCIsImh0dHBzOi8vYXBpLnNhaGhhLmFpL2NsYWltcy9yZWdpb24iOiJVUyIsImV4cCI6MTc0MjczNDY1NCwiaXNzIjoiaHR0cHM6Ly9zYWhoYS1wcm9kdWN0aW9uLmF1LmF1dGgwLmNvbS8iLCJhdWQiOiJodHRwczovL3NhaGhhLXByb2R1Y3Rpb24uYXUuYXV0aDAuY29tL2FwaS92Mi8ifQ.pjZh14_e940c-8gI1NednXZknHtBGzSpPIYfQ00hflE"
}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    data_scores = response.json()
    print("Données récupérées avec succès.")
else:
    print("Erreur lors de la récupération des données :", response.status_code, response.text)
    sys.exit(1)

conn = sqlite3.connect('/Users/camcam/Documents/taffpro/filsrouge/fils-rouge/database/sahha_scores.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS scores (
    id TEXT PRIMARY KEY,
    category_id INTEGER,
    state TEXT NOT NULL,
    score REAL NOT NULL,
    scoreDateTime TEXT NOT NULL,
    createdAtUtc TEXT NOT NULL,
    version INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS factors (
    id TEXT PRIMARY KEY,
    score_id TEXT NOT NULL,
    name TEXT NOT NULL,
    value REAL NOT NULL,
    goal REAL NOT NULL,
    score REAL NOT NULL,
    state TEXT NOT NULL,
    unit TEXT NOT NULL,
    FOREIGN KEY (score_id) REFERENCES scores(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS data_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    score_id TEXT NOT NULL,
    dataSource TEXT NOT NULL,
    FOREIGN KEY (score_id) REFERENCES scores(id)
)
''')

def get_or_create_category(category_name):
    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
        conn.commit()
        return cursor.lastrowid

def inserer_score(score):
    category_id = get_or_create_category(score['type'])
    
    # Check if the score already exists
    cursor.execute("SELECT id FROM scores WHERE id = ?", (score['id'],))
    existing_score = cursor.fetchone()
    
    if existing_score:
        print(f"Score with ID {score['id']} already exists. Skipping insertion.")
        return  # Skip insertion if the score already exists
    
    cursor.execute('''
    INSERT INTO scores (id, category_id, state, score, scoreDateTime, createdAtUtc, version)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        score['id'],
        category_id,
        score['state'],
        score['score'],
        score['scoreDateTime'],
        score['createdAtUtc'],
        score['version']
    ))
    
    for factor in score.get('factors', []):
        cursor.execute('''
        INSERT INTO factors (id, score_id, name, value, goal, score, state, unit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            factor['id'],
            score['id'],
            factor['name'],
            factor['value'],
            factor['goal'],
            factor['score'],
            factor['state'],
            factor['unit']
        ))
    
    for ds in score.get('dataSources', []):
        cursor.execute('''
        INSERT INTO data_sources (score_id, dataSource)
        VALUES (?, ?)
        ''', (
            score['id'],
            ds
        ))
    conn.commit()

for score in data_scores:
    inserer_score(score)

print("Insertion terminée.")

cursor.execute("SELECT s.id, c.name, s.score FROM scores s JOIN categories c ON s.category_id = c.id")
rows = cursor.fetchall()
for row in rows:
    print("Score ID:", row[0], "- Catégorie:", row[1], "- Score:", row[2])

conn.close()