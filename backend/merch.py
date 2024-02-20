from flask import Flask, jsonify, g, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from calculations import calculate_gross, calculate_net, calculate_total_owed, calculate_artist_revenue, calculate_house_due
import os
from auth import requires_auth

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
    auth0_id = db.Column(db.String(255), unique=True, nullable=False)

class InventoryItem(db.Model):
    __tablename__ = 'items'
    item_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    size = db.Column(db.String(50))
    price = db.Column(db.Float, nullable=False)
    count_in = db.Column(db.Integer, nullable=False)
    count_out = db.Column(db.Integer, nullable=False)
    comps = db.Column(db.Integer)
    item_type = db.Column(db.String(50), nullable=False)

class Configuration(db.Model):
    __tablename__ = 'configuration'
    configuration_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)   
    tax_rate = db.Column(db.Float, nullable=False)
    hard_cut = db.Column(db.Float, nullable=False)
    soft_cut = db.Column(db.Float, nullable=False)
    added_fees = db.Column(db.Float)

class SalesSummary(db.Model):
    __tablename__ = 'sales_summary'
    summary_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    total_gross = db.Column(db.Float, nullable=False)
    soft_gross = db.Column(db.Float, nullable=False)
    hard_gross = db.Column(db.Float, nullable=False)
    soft_owed_casino = db.Column(db.Float, nullable=False)
    hard_owed = db.Column(db.Float, nullable=False)
    house_due = db.Column(db.Float, nullable=False)
    artist_revenue = db.Column(db.Float, nullable=False)

class CreditCardInfo(db.Model):
    __tablename__ = 'credit_card_info'
    cc_info_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    cc_fee = db.Column(db.Float, nullable=False)
    cc_percentage = db.Column(db.Float)
    cc_sales = db.Column(db.Float)


@app.route('/inventory', methods=['POST'])
@requires_auth
def add_item():
    if not request.json:
        abort(400, description="Request must be in JSON")

    required_fields = ['description', 'size', 'price', 'count_in', 'count_out', 'comps', 'item_type']
    if not all(field in request.json for field in required_fields):
        abort(400, description=f"Missing fields in request data. Required fields are: {', '.join(required_fields)}")


    user_id = g.current_user['sub']
    user = User.query.filter_by(auth0_id=user_id).first()
    if not user:
        abort(404, description="User not found")

    new_item = InventoryItem(
        user_id=user.user_id,
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

    return jsonify({'message': 'Item added successfully', 'item id': new_item.item_id, 'description': new_item.description, 'size': new_item.size, 'price': new_item.price, 'count in': new_item.count_in, 'count out': new_item.count_out, 'comps': new_item.comps, 'item type': new_item.item_type}), 201
    # GET RID OF ITEM ID DISPLAY AFTER DEVELOPMENT IS DONE


@app.route('/inventory/<int:item_id>', methods=['PUT'])
@requires_auth
def update_item(item_id):
    user_id = g.current_user['sub']
    user = User.query.filter_by(auth0_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    item = InventoryItem.query.filter_by(item_id=item_id, user_id=user.user_id).first()
    if not item:
        return jsonify({'error': 'Item not found or you do not have permission to access this item'}), 404

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

    db.session.commit()

    return jsonify({'message': 'Item updated successfully', 'item id': item.item_id, 'description': item.description}), 200


@app.route('/inventory/<int:item_id>', methods=['DELETE'])
@requires_auth
def delete_item(item_id):
    user_id = g.current_user['sub']
    user = User.query.filter_by(auth0_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    item = InventoryItem.query.filter_by(item_id=item_id, user_id=user.user_id).first()

    if item is None:
        return jsonify({'error': 'Item not found'})

    db.session.delete(item)
    db.session.commit()

    return jsonify({'message': 'Item deleted successfully'})


@app.route('/inventory/delete_all', methods=['DELETE'])
@requires_auth
def delete_all():
    user_id = g.current_user['sub']
    user = User.query.filter_by(auth0_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        num_deleted = InventoryItem.query.filter_by(user_id=user.user_id).delete()
        db.session.commit()
        return jsonify({'message': f'Successfully deleted {num_deleted} items'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete items', 'details': str(e)}), 500

@app.route('/inventory/save_all', methods=['POST'])
@requires_auth
def save_all():
    user_id = g.current_user['sub']
    user = User.query.filter_by(auth0_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404


    items_data = request.json.get('items', [])
    new_items = []
    updated_items = 0

    for item_data in items_data:
        item_id = item_data.get('item_id')
        if item_id:
            item = InventoryItem.query.filter_by(item_id=item_id, user_id=user.user_id).first()
            if item:
                item.description = item_data.get('description', item.description)
                item.size = item_data.get('size', item.size)
                item.price = item_data.get('price', item.price)
                item.count_in = item_data.get('count_in', item.count_in)
                item.count_out = item_data.get('count_out', item.count_out)
                item.comps = item_data.get('count_out', item.comps)
                item.item_type = item_data.get('item_type', item.item_type)
                updated_items += 1
        else:
            new_item = InventoryItem(
                description=item_data.get('description'),
                size=item_data.get('size'),
                price=item_data.get('price'),
                count_in=item_data.get('count_in'),
                count_out=item_data.get('count_out'),
                comps=item_data.get('comps'),
                item_type=item_data.get('item_type')
            )
            new_items.append(new_item)
    
    db.session.add_all(new_items)
    db.session.commit()

    return jsonify({
        'message': 'Items saved successfully',
        'new_items_added': len(new_items),
        'items_updated': updated_items
    }), 200


@app.route('/inventory', methods=['GET'])
@requires_auth
def get_inventory():
    user_id = g.current_user['sub']
    user = User.query.filter_by(auth0_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    items = InventoryItem.query.filter_by(user_id=user.user_id).all()
    
    items_list = [{
                  'id': item.item_id,
                  'description': item.description,
                  'size': item.size,
                  'price': item.price,
                  'count_in': item.count_in,
                  'count_out': item.count_out,
                  'comps': item.comps,
                  'item_type': item.item_type
    } for item in items]
    return jsonify({'inventory': items_list})


@app.route('/credit-card-info', methods=['POST'])
@requires_auth
def add_credit_card_info():
    user_id = g.current_user['sub']
    user = User.query.filter_by(auth0_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not request.json:
        abort(400, "Request must be in JSON")
    # Only cc_fee is required; cc_percentage and cc_sales are optional
    if 'cc_fee' not in request.json:
        abort(400, "Missing required field: cc_fee")

    new_cc_info = CreditCardInfo(
        user_id=user.user_id,
        cc_fee=request.json['cc_fee'],
        cc_percentage=request.json.get('cc_percentage', None),  # Default to None if not provided
        cc_sales=request.json.get('cc_sales', None)  # Default to None if not provided
    )
    
    db.session.add(new_cc_info)
    db.session.commit()

    return jsonify({'message': 'Credit card info added successfully', 'cc_info_id': new_cc_info.cc_info_id}), 201


@app.route('/credit-card-info/<int:cc_info_id>', methods=['PUT'])
@requires_auth
def update_credit_card_info(cc_info_id):
    user_id = g.current_user['sub']
    user = User.query.filter_by(auth0_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404


    cc_info = CreditCardInfo.query.filter_by(cc_info_id=cc_info_id, user_id=user.user_id).first()
    if cc_info is None:
        return jsonify({'error': 'Credit card info not found'}), 404

    if not request.json:
        return jsonify({'error': 'Request must be in JSON'}), 400

    if 'cc_fee' in request.json:
        cc_info.cc_fee = request.json['cc_fee']

    # Only update cc_percentage and cc_sales if they are explicitly provided
    if 'cc_percentage' in request.json:
        cc_info.cc_percentage = request.json['cc_percentage']
    if 'cc_sales' in request.json:
        cc_info.cc_sales = request.json['cc_sales']

    db.session.commit()

    return jsonify({'message': 'Credit card info updated successfully'}), 200


@app.route('/configuration', methods=['POST'])
@requires_auth
def add_configuration():
    user_id = g.current_user['sub']
    user = User.query.filter_by(auth0_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not request.json:
        abort(400, "Request must be in JSON")

    required_fields = ['tax_rate','hard_cut','soft_cut']
    if not all(field in request.json for field in required_fields):
        abort(400, description=f"Missing fields in request data. Required fields are: {', '.join(required_fields)}")


    new_config = Configuration(
        tax_rate = request.json['tax_rate'],
        hard_cut = request.json['hard_cut'],
        soft_cut = request.json['soft_cut'],
        added_fees = request.json.get('added_fees', None) # Default to None if not provided
    )

    db.session.add(new_config)
    db.session.commit()

    return jsonify({'message': 'Configuration added successfully', 'New config ID': new_config.configuration_id}), 200


@app.route('/configuration/<int:configuration_id>', methods=['PUT'])
@requires_auth
def update_configuration(configuration_id):
    user_id = g.current_user['sub']
    user = User.query.filter_by(auth0_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404


    config = Configuration.query.filter_by(configuration_id=configuration_id, user_id=user.user_id).first()
    if config is None:
        return jsonify({'error': 'Configuration not found'}), 404

    if not request.json:
        return jsonify({'error': 'Request must be in JSON'}), 400

    if 'tax_rate' in request.json:
        config.tax_rate = request.json['tax_rate']
    if 'hard_cut' in request.json:
        config.hard_cut = request.json['hard_cut']
    if 'soft_cut' in request.json:
        config.soft_cut = request.json['soft_cut']
    if 'added_fees' in request.json:
        config.added_fees= request.json['added_fees']

    db.session.commit()

    return jsonify({'message': 'Configuration updated successfully'}), 200


@app.route('/calculate', methods=['GET'])
@requires_auth
def calculate_summary():
    user_id = g.current_user['sub']
    user = User.query.filter_by(auth0_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    items = InventoryItem.query.filter_by(user_id=user.user_id).all()
    config = Configuration.query.filter_by(user_id=user.user_id).first()
    cc_info = CreditCardInfo.query.filter_by(user_id=user.user_id).first()

    if not config:
        return jsonify({'error': 'Configuration not found'}), 404
    if not cc_info:
        return jsonify({'error': 'Credit Card info not found'}), 404
    if not items:
        return jsonify({'error': 'No inventory items found'}), 404

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
    
    tax_rate = config.tax_rate
    soft_cut = config.soft_cut
    hard_cut = config.hard_cut
    added_fees = config.added_fees
    credit_card_fee = cc_info.cc_fee if cc_info else 0

    total_gross = calculate_gross(items_data)
    soft_gross = calculate_gross(items_data, 'Soft')
    hard_gross = calculate_gross(items_data, 'Hard')
    soft_net = calculate_net(soft_gross, tax_rate, credit_card_fee)
    hard_net = calculate_net(hard_gross, tax_rate, credit_card_fee)
    soft_owed = calculate_total_owed(soft_net, soft_cut)
    hard_owed = calculate_total_owed(hard_net, hard_cut)
    total_house_due = calculate_house_due(soft_owed, hard_owed, added_fees)
    artist_revenue = calculate_artist_revenue(total_gross, tax_rate, total_house_due)
    
    return jsonify({
        'total_gross': total_gross,
        'soft_gross': soft_gross,
        'hard_gross': hard_gross,
        'soft_net': soft_net,
        'hard_net': hard_net,
        'soft_owed': soft_owed,
        'hard_owed': hard_owed,
        'house_due': total_house_due,
        'artist_revenue': artist_revenue
    }), 200


@app.route('/sales_summary', methods=['POST'])
@requires_auth
def add_sales_summary():
    user_id = g.current_user['sub']
    user = User.query.filter_by(auth0_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Assuming you send calculated data as JSON in the request body
    if not request.json:
        return jsonify({'error': 'Request must be in JSON format'}), 400

    new_summary = SalesSummary(
        user_id=user.user_id,
        total_gross=request.json['total_gross'],
        soft_gross=request.json['soft_gross'],
        hard_gross=request.json['hard_gross'],
        soft_owed=request.json['soft_owed'],
        hard_owed=request.json['hard_owed'],
        house_due=request.json['house_due'],
        artist_revenue=request.json['artist_revenue']
    )
    db.session.add(new_summary)
    db.session.commit()
    return jsonify({'message': 'Sales summary added successfully', 'summary_id': new_summary.summary_id}), 201


@app.route('/sales_summary/<int:summary_id>', methods=['PUT'])
@requires_auth
def update_sales_summary(summary_id):
    user_id = g.current_user['sub']
    user = User.query.filter_by(auth0_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    sales_summary = SalesSummary.query.filter_by(user_id=user.user_id, summary_id=summary_id).first()
    if not sales_summary:
        return jsonify({'error': 'Sales summary not found'}), 404

    data = request.json
    total_gross = data.get('total_gross')
    soft_gross = data.get('soft_gross')
    hard_gross = data.get('hard_gross')
    soft_owed = data.get('soft_owed')
    hard_owed = data.get('hard_owed')
    house_due = data.get('house_due')
    artist_revenue = data.get('artist_revenue')

    if total_gross:
        sales_summary.total_gross = total_gross
    if soft_gross:
        sales_summary.soft_gross = soft_gross
    if hard_gross:
        sales_summary.hard_gross = hard_gross
    if soft_owed:
        sales_summary.soft_owed = soft_owed
    if hard_owed:
        sales_summary.hard_owed = hard_owed
    if house_due:
        sales_summary.house_due = house_due
    if artist_revenue:
        sales_summary.artist_revenue = artist_revenue

    db.session.commit()
    return jsonify({'message:': 'Sales summary updated successfully'}), 201


if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False') == 'True', host='0.0.0.0')

