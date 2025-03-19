import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

def load_data_from_db():
    conn = sqlite3.connect('user_data.db')
    query = "SELECT active_hours, steps, recommendation_score FROM metrics"
    data = pd.read_sql_query(query, conn)
    conn.close()
    return data

def train_model():
    data = load_data_from_db()
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

if __name__ == "__main__":
    model = train_model()