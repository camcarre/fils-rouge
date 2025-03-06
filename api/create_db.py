import sqlite3

def create_database():
    conn = sqlite3.connect('user_data.db')  
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
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
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
