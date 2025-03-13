import requests
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)

API_URL = 'https://sandbox-api.sahha.ai/api/v1/profile/biomarker/WAJDbLDMeZWbT3AAYEJOE49Ijlg2'
HEADERS = {
    'Authorization': 'account eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwczovL2FwaS5zYWhoYS5haS9jbGFpbXMvYWNjb3VudElkIjoiYzg4NDY0ZTItODU2Ny00MGE0LWE1MmItYjhmNTBlYzAyMTAxIiwiaHR0cHM6Ly9hcGkuc2FoaGEuYWkvY2xhaW1zL2FkbWluIjoiVHJ1ZSIsImh0dHBzOi8vYXBpLnNhaGhhLmFpL2NsYWltcy9hY2NvdW50IjoiVHJ1ZSIsImh0dHBzOi8vYXBpLnNhaGhhLmFpL2NsYWltcy9zYWhoYUFwaVNjb3BlIjoiU2FuZGJveCIsImh0dHBzOi8vYXBpLnNhaGhhLmFpL2NsYWltcy9yZWdpb24iOiJVUyIsImV4cCI6MTc0MzM0NjU4NiwiaXNzIjoiaHR0cHM6Ly9zYWhoYS1wcm9kdWN0aW9uLmF1LmF1dGgwLmNvbS8iLCJhdWQiOiJodHRwczovL3NhaGhhLXByb2R1Y3Rpb24uYXUuYXV0aDAuY29tL2FwaS92Mi8ifQ.a7GjS9tKKHCHdGgRYGmqNIOosEf5Io2werEiikHo1mc',
}

params = {
    'startDateTime': '2025-02-27T23:00:00.000Z',
    'endDateTime': '2025-03-05T23:00:00.000Z',
    'types': ['steps', 'active_hours', 'active_duration', 'active_energy_burned', 'total_energy_burned', 'height', 'weight', 'resting_energy_burned', 'age', 'biological_sex', 'date_of_birth', 'sleep_start_time', 'sleep_end_time', 'sleep_duration', 'sleep_debt', 'sleep_interruptions', 'sleep_in_bed_duration', 'sleep_awake_duration', 'sleep_regularity'],
    'categories': ['activity', 'body', 'characteristic', 'sleep']
}

response = requests.get(API_URL, headers=HEADERS, params=params)

if response.status_code == 200:
    data = response.json()
    logging.info('Data fetched successfully from the API.')
    conn = sqlite3.connect('/Users/camcam/Documents/taffpro/fils-rouge/api/user_data.db')
    c = conn.cursor()
    c.execute('DELETE FROM metrics')
    for item in data:
        user_id = 1  
        c.execute('''INSERT INTO metrics (user_id, category, type, periodicity, aggregation, value, unit, valueType, startDateTime, endDateTime)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (user_id, item.get('category', 'N/A'), item.get('type', 'N/A'), item.get('periodicity', 'N/A'), item.get('aggregation', 'N/A'), item.get('value', 'N/A'), item.get('unit', 'N/A'), item.get('valueType', 'N/A'), item['startDateTime'], item['endDateTime']))
    conn.commit()
    conn.close()
    logging.info('Metrics table cleared and data inserted successfully.')
else:
    logging.error(f'Error: {response.status_code} - {response.text}')
