def determine_plan_details(plan_id):
    plans = {
        'essential': {'name': 'Essential_Plan', 'price': '$210.00'},
        'enhanced': {'name': 'Enhanced_Plan', 'price': '$410.00'},
        'elite': {'name': 'Elite_Plan', 'price': '$680.00'},
        'plus': {'name': 'Plus_Plan', 'price': '$950.00'}
    }

    plan_details = plans.get(plan_id)

    if not plan_details:
        raise ValueError("Invalid plan selected.")

    return plan_details


def extract_payment_method(card_number):
    if card_number.startswith('4'):
        card_type = "Visa"
    elif card_number.startswith('5'):
        card_type = "MasterCard"
    elif card_number.startswith('3'):
        card_type = "American Express"
    else:
        card_type = "Unknown"

    return f"{card_type} ****{card_number[-4:]}"
