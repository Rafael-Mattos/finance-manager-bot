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
    

    def get_all_categories(self):
        url = f'{self.DOMAIN}/api/v1/categories/'

        response = requests.get(url, headers=self.get_headers())
        return response.json()


    def insert_category(self, category, is_expense: bool):
        if not isinstance(is_expense, bool):
            return {'error': 'O valor passado para o parâmetro "is_expense" deve ser do tipo bool.'}
        
        url = f'{self.DOMAIN}/api/v1/categories/'
        info = {
            'name': category,
            'type': 'e' if is_expense else 'r'
        }

        response = requests.post(url, headers=self.get_headers(), json=info)
        return response.json()
    

    def patch_category(self, id, category):
        url = f'{self.DOMAIN}/api/v1/categories/{id}/'
        info = {
            'name': category
        }

        response = requests.patch(url, headers=self.get_headers(), json=info)
        return response.json()
    

    def delete_category(self, id):
        url = f'{self.DOMAIN}/api/v1/categories/{id}/'

        response = requests.delete(url, headers=self.get_headers())

        if response.status_code == 204:
            return {"detail": "Categoria deletada com sucesso."}
        elif response.status_code == 500:
            return {
                "detail": "Exclusão não é permitida. Verifique se existem descrições atreladas a esta categoria."
            }
        return {"error": "Nenhuma categoria encontrada."}


    def get_top_descriptions(self):
        url = f'{self.DOMAIN}/api/v1/transactions/top-descriptions/'
        response = requests.get(url, headers=self.get_headers())
        return response.json()
    

    def get_all_descriptions(self):
        url = f'{self.DOMAIN}/api/v1/descriptions/'

        response = requests.get(url, headers=self.get_headers())
        return response.json()
    

    def insert_description(self, category_id, description):
        url = f'{self.DOMAIN}/api/v1/descriptions/'
        info = {
            'category': category_id,
            'name': description
        }

        response = requests.post(url, headers=self.get_headers(), json=info)
        return response.json()
    

    def put_description(self, id, category_id, description):
        url = f'{self.DOMAIN}/api/v1/descriptions/{id}/'
        info = {
            'category': category_id,
            'name': description
        }

        response = requests.put(url, headers=self.get_headers(), json=info)
        return response.json()
    

    def delete_description(self, id):
        url = f'{self.DOMAIN}/api/v1/descriptions/{id}/'
        response = requests.delete(url, headers=self.get_headers())

        if response.status_code == 204:
            return {"detail": "Descrição deletada com sucesso."}
        elif response.status_code == 500:
            return {
                "detail": "Exclusão não é permitida. Verifique se existem transações atreladas a esta descrição."
            }
        return {"error": "Nenhuma descrição encontrada."}
    

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
    

    def get_transaction_by_condition(self, rql_condition):
        url = f'{self.DOMAIN}/api/v1/transactions/?{rql_condition}'
        response = requests.get(url, headers=self.get_headers())
        return response.json()
    

    def patch_transaction(self, id, key, value):
        url = f'{self.DOMAIN}/api/v1/transactions/{id}/'

        info = {
            key: value
        }

        response = requests.patch(url, headers=self.get_headers(), json=info)
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
