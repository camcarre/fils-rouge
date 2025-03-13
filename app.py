import logging
from flask import Flask, render_template
import sqlite3

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def index():
    logging.info('Fetching metrics data from the database.')
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM metrics')
    metrics = c.fetchall()
    conn.close()
    logging.info('Metrics data fetched successfully.')
    return render_template('index.html', metrics=metrics)

if __name__ == '__main__':
    logging.info('Starting Flask application on port 5002.')
    app.run(debug=True, port=5008)
