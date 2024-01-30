from flask import Flask, jsonify, request
import mysql.connector
import os

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host = os.environ.get('DB_HOST','localhost'),
        user = os.environ.get('DB_USER', 'root'),
        password = os.environ.get('DB_PASSWORD', 'defaultpassword'),
        database = os.environ.get('DB_NAME', 'ninoDB')
    )

@app.route('/')
def index():
    return "Welcome to Nino"

#add more routes here

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

