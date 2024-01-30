from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}"
    f"@{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    size = db.Column(db.String(50))
    price = db.Column(db.Float)
    count_in = db.Column(db.Integer)
    count_out = db.Column(db.Integer)
    comps = db.Column(db.Integer)
    item_type = db.Column(db.String(50))

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'error': 'Missing username, email, or password'}), 400

    # Check if user already exists
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({'error': 'Username or email already exists'}), 409

    # Create new user
    new_user = User(username=username, email=email)
    new_user.set_password(password)

    # Add new user to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    # Logic for user login
    return jsonify({'message': 'Login successful'})

@app.route('/inventory', methods=['POST'])
def add_item():
    # Logic for adding an item
    return jsonify({'message': 'Item added successfully'}), 201

@app.route('/inventory/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    # Logic for updating an item
    return jsonify({'message': 'Item updated successfully'})

@app.route('/inventory/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    # Logic for deleting an item
    return jsonify({'message': 'Item deleted successfully'})

@app.route('/inventory', methods=['GET'])
def get_inventory():
    # Logic for getting the user's inventory
    return jsonify({'inventory': []})

@app.route('/calculate', methods=['POST'])
def calculate_summary():
    # Logic for calculating financial summaries
    return jsonify({'summary': {}})

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')

