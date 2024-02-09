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
    item = InventoryItem.query.get(item_id)

    if item is None:
        return jsonify({'error': 'Item not found'}), 404

    if not request.json:
        return jsonify({'error': 'Request must be in JSON'}), 400
    
    data = request.json
    description = data.get('description')
    size = data.get('size')
    price = data.get('price')
    count_in = data.get('count_in')
    count_out = data.get('count_out')
    comps = data.get('comps')
    item_type = data.get('item_type')

    if description:
        item.description = description
    if size:
        item.size = size
    if price is not None:
        item.price = price
    if count_in is not None:
        item.count_in = count_in
    if count_out is not None:
        item.count_out = count_out
    if comps is not None:
        item.comps = comps
    if item_type:
        item.item_type = item_type

    db.sessions.commit()

    return jsonify({'message': 'Item updated successfully'}), 200

@app.route('/inventory/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = InventoryItem.query.get(item_id)

    if item is None:
        return jsonify({'error': 'Item not found'})

    db.session.delete(item)
    db.session.commit()

    return jsonify({'message': 'Item deleted successfully'})

@app.route('/inventory', methods=['GET'])
def get_inventory():
    items = InventoryItem.query.all()
    
    items_list = [{
                  'id': item.id,
                  'description': item.description,
                  'size': item.size,
                  'count_in': item.count_in,
                  'count_out': item.count_out,
                  'comps': item.comps,
                  'item_type': item.item_type
    } for item in items]
    return jsonify({'inventory': items_list})

@app.route('/calculate', methods=['POST'])
def calculate_summary():
    # Logic for calculating financial summaries
    return jsonify({'summary': {}})

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False') == 'True', host='0.0.0.0')

