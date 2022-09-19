import requests

from .BaseSalaryService import BaseSalaryService


class HHSalaryService(BaseSalaryService):
    def predict_rub_salary(self, vacancy):
        salary = vacancy['salary']

        if salary['currency'] != 'RUR':
            return None

        return BaseSalaryService.predict_rub_salary_util(salary['from'], salary['to'])

    def get_vacancies_by_language(self, language):
        url = 'https://api.hh.ru/vacancies'
        moscow_area_id = 1
        params = {
            'text': language,
            'area': moscow_area_id,
            'only_with_salary': True,
            'per_page': 100
        }

        has_next = True
        vacancies = []
        page = 0
        total = 0

        while has_next:
            params['page'] = page
            response = requests.get(url, params=params)
            response.raise_for_status()
            vacancies_search_result = response.json()

            pages = vacancies_search_result['pages']
            vacancies += vacancies_search_result['items']
            total = vacancies_search_result['found']
            page += 1
            has_next = page < pages

        return {
            'vacancies': vacancies,
            'total': total
        }
