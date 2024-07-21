import requests
from decimal import Decimal
from app.environment import Environment


base_url = 'https://api.paystack.co/transaction/'
headers = {
    'Authorization': f'Bearer {Environment.PAYSTACK_SK}',
    'Content_Type': 'application/json',
}

def make_payment(user, repayment):
    url = base_url + 'initialize'
    amount = repayment.get('repay_amount')
    reference = repayment.get('id')
    
    data = {
        'email': user.email,
        'amount': int(Decimal(amount) * 100),  # subunit of NGN (100 kobo)
        'reference':  reference,
    }

    response = requests.post(url, headers=headers, json=data)
    return response


def verify_payment(reference):
    url = base_url + f"verify/{reference}"

    response = requests.get(url, headers=headers)

    return response
