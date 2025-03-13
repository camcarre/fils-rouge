import sqlite3
import logging

logging.basicConfig(level=logging.INFO)

def create_database():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                age INTEGER,
                sexe INTEGER,
                poids REAL,
                taille INTEGER,
                objectif TEXT,
                activite TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    logging.info('Users table created or already exists.')
    c.execute('''CREATE TABLE IF NOT EXISTS metrics (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                category VARCHAR(50) NOT NULL,
                type VARCHAR(50) NOT NULL,
                periodicity VARCHAR(50) NOT NULL,
                aggregation VARCHAR(50) NOT NULL,
                value TEXT NOT NULL,
                unit VARCHAR(50) NOT NULL,
                valueType VARCHAR(50) NOT NULL,
                startDateTime TIMESTAMP NOT NULL,
                endDateTime TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS recommendations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                advice TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )''')
    # Insérer des données de test pour les utilisateurs
    c.execute("INSERT INTO users (id, name, email, age, sexe, poids, taille, objectif, activite) VALUES ('1', 'Test User', 'test@example.com', 25, 0, 70, 175, 'perte de poids', 'moderee')")
    # Insérer des données de test pour les métriques
    c.execute("INSERT INTO metrics (id, user_id, category, type, periodicity, aggregation, value, unit, valueType, startDateTime, endDateTime) VALUES ('1', '1', 'sommeil', 'durée', 'quotidien', 'moyenne', '7', 'heures', 'nombre', '2025-03-01 00:00:00', '2025-03-01 23:59:59')")
    conn.commit()
    conn.close()
    logging.info('Database setup complete.')

if __name__ == '__main__':
    create_database()
