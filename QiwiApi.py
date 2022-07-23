import random
from datetime import datetime, timedelta
import requests


class Wallet:
    def __init__(self, token: str, secret_key: str = None):
        self.token = token
        self.secret_key = secret_key

    def get_headers(self):
        headers = {
            'Accept': 'application/json',
            'Content-type': 'application/json',
            'Authorization': f'Bearer {self.token}',
        }
        return headers

    def edit_token(self, token: str):
        self.token = token

    def edit_secret_key(self, secret_key: str):
        self.secret_key = secret_key

    def get_me(self):
        url = 'https://edge.qiwi.com/person-profile/v1/profile/current?authInfoEnabled=false'
        response = requests.get(url, headers=self.get_headers())
        return response.json()

    def get_info_about_me(self):
        url = f"https://edge.qiwi.com/identification/v1/persons/"\
              f"{self.get_me()['contractInfo']['contractId']}/identification"
        response = requests.get(url, headers=self.get_headers())
        return response.json()

    def get_list_of_payments(self, rows: int = 10):
        url = f"https://edge.qiwi.com/payment-history/v2/persons/"\
              f"{self.get_me()['contractInfo']['contractId']}/payments?rows={rows}"
        response = requests.get(url, headers=self.get_headers())
        # for get list_of_payments use ['data']
        return response.json()

    def get_info_about_transaction(self, txnid):
        url = f"https://edge.qiwi.com/payment-history/v2/transactions/{txnid}"
        response = requests.get(url, headers=self.get_headers())
        return response.json()

    def new_bill(self, amount: int, billid=random.randint(100000, 10000000), comment: str = None):
        if self.secret_key is None:
            print('Secret key не указан')
            return
        headers = {
            'Accept': 'application/json',
            'Content-type': 'application/json',
            'Authorization': f'Bearer {self.secret_key}',
        }

        json = {
            "amount": {
                "currency": "RUB",
                "value": str(amount) + '.00'
            },
            "expirationDateTime": self.get_date(plus=60),
            "comment": comment
        }

        url = f"https://api.qiwi.com/partner/bill/v1/bills/{billid}"
        response = requests.put(url, json=json, headers=headers)
        return response.json()

    def get_info_bill(self, billid):
        if self.secret_key is None:
            print('Secret key не указан')
            return
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.secret_key}',
        }
        url = f'https://api.qiwi.com/partner/bill/v1/bills/{billid}'
        response = requests.get(url, headers=headers)
        """
        ['status']['value'] for get status

        WAITING	Счет выставлен, ожидает оплаты	-
        PAID	Счет оплачен	+
        REJECTED	Счет отклонен	+
        EXPIRED	Время жизни счета истекло. Счет не оплачен	+
        """
        return response.json()

    @staticmethod
    def get_date(plus: int):
        o = str(datetime.now() + timedelta(plus)).split('.')
        n = o[0].split()
        s = n[0] + 'T' + n[1] + '+03:00'
        return s
