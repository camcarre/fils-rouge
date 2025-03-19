import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            weight FLOAT,
            height INTEGER,
            objective TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            active_hours REAL NOT NULL,
            steps INTEGER NOT NULL,
            recommendation_score REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

class User:
    def __init__(self, id, email, name, age=None, weight=None, height=None, objective=None):
        self.id = id
        self.email = email
        self.name = name
        self.age = age
        self.weight = weight
        self.height = height
        self.objective = objective

    @staticmethod
    def get_by_id(user_id):
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_data = c.fetchone()
        conn.close()
        
        if user_data:
            return User(
                id=user_data[0],
                email=user_data[1],
                name=user_data[3],
                age=user_data[4],
                weight=user_data[5],
                height=user_data[6],
                objective=user_data[7]
            )
        return None

    @staticmethod
    def get_by_email(email):
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user_data = c.fetchone()
        conn.close()
        
        if user_data:
            return User(
                id=user_data[0],
                email=user_data[1],
                name=user_data[3],
                age=user_data[4],
                weight=user_data[5],
                height=user_data[6],
                objective=user_data[7]
            )
        return None

    @staticmethod
    def create(email, password, name, age=None, weight=None, height=None, objective=None):
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO users (email, password_hash, name, age, weight, height, objective)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (email, generate_password_hash(password), name, age, weight, height, objective))
            conn.commit()
            user_id = c.lastrowid
            conn.close()
            return User.get_by_id(user_id)
        except sqlite3.IntegrityError:
            conn.close()
            return None

    def update(self, name=None, age=None, weight=None, height=None, objective=None):
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        
        updates = []
        values = []
        
        if name:
            updates.append('name = ?')
            values.append(name)
            self.name = name
        if age:
            updates.append('age = ?')
            values.append(age)
            self.age = age
        if weight:
            updates.append('weight = ?')
            values.append(weight)
            self.weight = weight
        if height:
            updates.append('height = ?')
            values.append(height)
            self.height = height
        if objective:
            updates.append('objective = ?')
            values.append(objective)
            self.objective = objective
            
        if updates:
            values.append(self.id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            c.execute(query, values)
            conn.commit()
            
        conn.close()
        return self

    @staticmethod
    def verify_password(email, password):
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute('SELECT password_hash FROM users WHERE email = ?', (email,))
        result = c.fetchone()
        conn.close()
        
        if result and check_password_hash(result[0], password):
            return True
        return False

def load_data_from_db(user_id):
    conn = sqlite3.connect('user_data.db')
    query = "SELECT active_hours, steps, recommendation_score FROM metrics WHERE user_id = ?"
    data = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return data

def train_model(user_id):
    data = load_data_from_db(user_id)
    X = data[['active_hours', 'steps']]
    y = data['recommendation_score']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    print(f'Mean Squared Error: {mse}')

    return model

def generate_recommendations(model, user_data):
    prediction = model.predict(user_data[['active_hours', 'steps']])
    return prediction

init_db()

if __name__ == "__main__":
    user = User.create('example@example.com', 'password', 'John Doe')
    model = train_model(user.id)