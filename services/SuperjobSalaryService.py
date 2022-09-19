import requests

from .BaseSalaryService import BaseSalaryService


class SuperjobSalaryService(BaseSalaryService):
    def __init__(self, languages, title, api_key):
        BaseSalaryService.__init__(self, languages, title)
        self.api_key = api_key

    def predict_rub_salary(self, vacancy):
        return BaseSalaryService.predict_rub_salary_util(vacancy['payment_from'], vacancy['payment_to'])

    def get_vacancies_by_language(self, language):
        url = 'https://api.superjob.ru/2.0/vacancies'
        params = {
            'town': 'Москва',
            'keyword': language,
            'count': 100
        }
        headers={'X-Api-App-Id': self.api_key}

        has_next = True
        vacancies = []
        page = 0
        total = 0

        while has_next:
            params['page'] = page
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            vacancies_search_result = response.json()

            more = vacancies_search_result['more']
            vacancies += vacancies_search_result['objects']
            total = vacancies_search_result['total']
            page += 1
            has_next = more

        return {
            'vacancies': vacancies,
            'total': total
        }
