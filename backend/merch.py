from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from calculations import calculate_item_gross, calculate_gross, calculate_net, calculate_total_owed, calculate_band_revenue, calculate_house_due
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db, directory= 'db/migrations')

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    auth0_id = db.Column(db.String(255), unique=True, nullable=False)  # New field for Auth0 user ID

class InventoryItem(db.Model):
    __tablename__ = 'items'
    item_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    size = db.Column(db.String(50))
    price = db.Column(db.Float)
    count_in = db.Column(db.Integer)
    count_out = db.Column(db.Integer)
    comps = db.Column(db.Integer)
    item_type = db.Column(db.String(50))

class Configuration(db.Model):
    __tablename__ = 'configuration'
    configuration_id = db.Column(db.Integer, primary_key=True)
    tax_rate = db.Column(db.Float, nullable=False)
    hard_cut = db.Column(db.Float, nullable=False)
    soft_cut = db.Column(db.Float, nullable=False)
    added_fees = db.Column(db.Float)

class SalesSummary(db.Model):
    __tablename__ = 'sales_summary'
    summary_id = db.Column(db.Integer, primary_key=True)
    total_gross = db.Column(db.Float)
    total_soft_gross = db.Column(db.Float)
    total_hard_gross = db.Column(db.Float)
    total_soft_owed_casino = db.Column(db.Float)
    total_hard_owed_casino = db.Column(db.Float)
    total_owed_casino = db.Column(db.Float)
    band_revenue_received = db.Column(db.Float)

class CreditCardInfo(db.Model):
    __tablename__ = 'credit_card_info'
    cc_info_id = db.Column(db.Integer, primary_key=True)
    sales_summary_id = db.Column(db.Integer, db.ForeignKey('sales_summary.summary_id'))
    cc_fee = db.Column(db.Float, nullable=False)
    cc_percentage = db.Column(db.Float)
    cc_sales = db.Column(db.Float)

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
                  'price': item.price,
                  'count_in': item.count_in,
                  'count_out': item.count_out,
                  'comps': item.comps,
                  'item_type': item.item_type
    } for item in items]
    return jsonify({'inventory': items_list})

@app.route('/calculate', methods=['GET'])
def calculate_summary():
    config = Configuration.query.first()

    items = InventoryItem.query.all()
    items_data = [
        {
            'description': item.description,
            'price': item.price,
            'count_in': item.count_in,
            'count_out': item.count_out,
            'comps': item.comps,
            'item_type': item.item_type
        } for item in items
    ]
    
    # Example values for tax rate and credit card fee
    tax_rate = config.tax_rate
    soft_cut = config.soft_cut
    hard_cut = config.hard_cut
    added_fees = config.added_fees
    credit_card_fee = 100

    total_gross = calculate_gross(items_data)
    soft_gross = calculate_gross(items_data, 'Soft')
    hard_gross = calculate_gross(items_data, 'Hard')
    soft_net = calculate_net(soft_gross, tax_rate, credit_card_fee)
    hard_net = calculate_net(hard_gross, tax_rate, credit_card_fee)
    soft_owed = calculate_total_owed(soft_net, soft_cut)
    hard_owed = calculate_total_owed(hard_net, hard_cut)
    total_house_due = calculate_house_due(soft_owed, hard_owed, added_fees)
    band_revenue = calculate_band_revenue(total_gross, tax_rate, total_house_due)
    
    return jsonify({
        'total_gross': total_gross,
        'soft_gross': soft_gross,
        'hard_gross': hard_gross,
        'soft_net': soft_net,
        'hard_net': hard_net,
        'soft_owed': soft_owed,
        'hard_owed': hard_owed,
        'total_house_due': total_house_due,
        'band_revenue': band_revenue
    }), 200

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False') == 'True', host='0.0.0.0')

