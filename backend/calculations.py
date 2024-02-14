# calculations.py

def calculate_item_gross(item):
    """Calculate the gross for an individual item."""
    return (item['count_in'] - item['comps'] - item['count_out']) * item['price']

def calculate_gross(items, item_type=None):
    """Calculate gross sales, optionally filtered by item type."""
    filtered_items = (item for item in items if item['item_type'] == item_type) if item_type else items
    return sum((item['count_in'] - item['comps'] - item['count_out']) * item['price'] for item in filtered_items)

def calculate_net(gross, tax_rate, credit_card_fee):
    """Calculate net sales after tax and credit card fees."""
    net_sales = gross / (1 + tax_rate / 100)
    return net_sales - credit_card_fee

def calculate_total_owed(net, cut_percentage):
    total_owed = net * (cut_percentage / 100)
    return total_owed

def calculate_artist_revenue(gross, tax_rate, total_owed):
    artist_revenue = gross / (1 + tax_rate / 100) - total_owed
    return artist_revenue

def calculate_house_due(soft_total_owed, hard_total_owed, fee):
    house_due = soft_total_owed + hard_total_owed + fee
    return house_due
