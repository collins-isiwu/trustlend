import requests
from app.environment import Environment


base_url = 'https://api.paystack.co/transaction/'
headers = {
    'Authorization': f'Bearer {Environment.PAYSTACK_SK}',
    'Content_Type': 'application/json',
}

def make_payment(data, user, loan_balance):
    pass