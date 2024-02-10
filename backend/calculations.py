# calculations.py

def get_gross_per_item(count_in, comps, count_out, price):
    """Calculate gross for a specific item."""
    return (count_in - comps - count_out) * price

def get_total_gross(items):
    """Calculate total gross for the entire inventory."""
    total_gross = sum(get_gross_per_item(item.count_in, item.comps, item.count_out, item.price) for item in items)
    return total_gross
