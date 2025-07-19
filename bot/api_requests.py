import os

from dotenv import load_dotenv
import requests


class ApiRequests:
    def __init__(self):
        load_dotenv()
        self.token = None
        self.DOMAIN = os.getenv("DOMAIN")


    def get_headers(self):
        TOKEN_REFRESH = os.getenv("REFRESH")

        if not self.token_is_valid():
            url = f'{self.DOMAIN}/api/v1/token/refresh/'
            response = requests.post(url, json={'refresh': TOKEN_REFRESH})

            if response.status_code == 200:
                self.token = response.json().get('access')
            else:
                self.token = None
        
        HEADERS = {
            "Authorization": f"Bearer {self.token}"
        }
        return HEADERS
        

    def token_is_valid(self):
        if self.token is None:
            return False
        
        try:
            url = f'{self.DOMAIN}/api/v1/token/verify/'
            response = requests.post(url, json={'token': self.token})

            if response.status_code == 200:
                return True
            
        except:
            return False

        return False


    def get_top_descriptions(self):
        url = f'{self.DOMAIN}/api/v1/transactions/top-descriptions/'
        response = requests.get(url, headers=self.get_headers())
        return response.json()
    

    def insert_transaction(self, category, description, amount, date=None, obs=None):
        url = f'{self.DOMAIN}/api/v1/transactions/'
        info = {
            'category': category,
            'description': description,
            'amount': amount,
        }

        if date:
            info['date'] = date
        if obs:
            info['obs'] = obs

        response = requests.post(url, headers=self.get_headers(), json=info)
        return response.json()
    

    def insert_recurring_transaction(self, category, description, amount, date=None, obs=None)


if __name__ == '__main__':
    teste = ApiRequests()
    print(teste.insert_transaction(4, 3, 150.57, '2025-07-18', 'Uma observação qualquer'))
