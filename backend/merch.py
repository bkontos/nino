
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db, directory= 'db/migrations')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    auth0_id = db.Column(db.String(255), unique=True, nullable=False)  # New field for Auth0 user ID

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    size = db.Column(db.String(50))
    price = db.Column(db.Float)
    count_in = db.Column(db.Integer)
    count_out = db.Column(db.Integer)
    comps = db.Column(db.Integer)
    item_type = db.Column(db.String(50))

@app.route('/inventory', methods=['POST'])
def add_item():
    if not request.json:
        abort(400, description="Request must be in JSON")

    required_fields = ['description', 'size', 'price', 'count_in', 'count_out', 'comps', 'item_type']
    if not all(field in request.json for field in required_fields):
        abort(400, description=f"Missing fields in request data. Required fields are: {', '.join(required_fields)}")

    new_item = InventoryItem(
        description = request.json['description'],
        size = request.json['size'],
        price = request.json['price'],
        count_in = request.json['count_in'],
        count_out = request.json['count_out'],
        comps = request.json['comps'],
        item_type = request.json['item_type']
    )
    
    db.session.add(new_item)
    db.session.commit()

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
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False') == 'True', host='0.0.0.0')

