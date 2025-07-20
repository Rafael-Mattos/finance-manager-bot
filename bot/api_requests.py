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
    

    def get_transaction(self, id):
        url = f'{self.DOMAIN}/api/v1/transactions/{id}/'
        response = requests.get(url, headers=self.get_headers())
        return response.json()
    

    def delete_transaction(self, id):
        url = f'{self.DOMAIN}/api/v1/transactions/{id}/'

        response = requests.delete(url, headers=self.get_headers())
        if response.status_code == 204:
            return {"detail": "Lançamento deletado com sucesso."}
        return {"error": "Nenhum lançamento encontrado"}
    

    def insert_recurring_transaction(self, category, description, amount, date=None, obs=None, repeat=None):
        url = f'{self.DOMAIN}/api/v1/transactions/recurring/'
        info = {
            'category': category,
            'description': description,
            'amount': amount,
        }

        if repeat:
            info['repeat'] = repeat
        if date:
            info['date'] = date
        if obs:
            info['obs'] = obs

        response = requests.post(url, headers=self.get_headers(), json=info)
        return response.json()
    

    def delete_recurring_transactions(self, reference_id, from_date):
        url = f'{self.DOMAIN}/api/v1/transactions/delete-from-date/'
        info = {
            "original_id": reference_id,
            "from_date": from_date
        }
        response = requests.delete(url, headers=self.get_headers(), json=info)
        return response.json()


if __name__ == '__main__':
    teste = ApiRequests()
    # print(teste.insert_transaction(3, 2, 200.57))
    print(teste.delete_transaction(4948))
    # print(teste.insert_recurring_transaction(1, 1, 70000, '2025-09-23', repeat=4))
    # print(teste.delete_recurring_transactions(4900, '2025-08-01'))
