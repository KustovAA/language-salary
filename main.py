from environs import Env
import requests
from terminaltables import AsciiTable


def predict_rub_salary(salary_from=None, salary_to=None):
    if salary_from and salary_to:
        return int((salary_from + salary_to) / 2)

    if salary_from:
        return int(salary_from * 1.2)

    if salary_to:
        return int(salary_to * 0.8)

    return None


def predict_rub_salary_for_hh(vacancy):
    salary = vacancy['salary']

    if salary['currency'] != 'RUR':
        return None

    return predict_rub_salary(salary['from'], salary['to'])


def predict_rub_salary_for_superjob(vacancy):
    return predict_rub_salary(vacancy['payment_from'], vacancy['payment_to'])


def get_vacancies_by_language_hh(language):
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


def get_vacancies_by_language_superjob(language, api_key):
    url = 'https://api.superjob.ru/2.0/vacancies'
    params = {
        'town': 'Москва',
        'keyword': language,
        'count': 100
    }
    headers={'X-Api-App-Id': api_key}

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


def get_average_salary_stat_hh(vacancies):
    count = 0
    amount = 0

    for vacancy in vacancies['vacancies']:
        salary = predict_rub_salary_for_hh(vacancy)
        if salary:
            count += 1
            amount += int(salary)

    return {
        'average_salary': int(amount / count) if count > 0 else 0,
        'vacancies_processed': count,
        'vacancies_found': vacancies['total']
    }


def get_average_salary_stat_superjob(vacancies):
    count = 0
    amount = 0

    for vacancy in vacancies['vacancies']:
        salary = predict_rub_salary_for_superjob(vacancy)
        if salary:
            count += 1
            amount += int(salary)

    return {
        'average_salary': int(amount / count) if count > 0 else 0,
        'vacancies_processed': count,
        'vacancies_found': vacancies['total']
    }


def get_superjob_salaries_table(languages, api_key):
    salaries_table = [
        ('Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата')
    ]

    for language in languages:
        stat = get_average_salary_stat_superjob(
            get_vacancies_by_language_superjob(language, api_key=api_key)
        )
        salaries_table.append(
            (language, stat['vacancies_found'], stat['vacancies_processed'], stat['average_salary'])
        )

    table = AsciiTable(salaries_table, 'SuperJob Moscow')
    return table.table


def get_hh_salaries_table(languages):
    salaries_table = [
        ('Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата')
    ]

    for language in languages:
        stat = get_average_salary_stat_hh(
            get_vacancies_by_language_hh(language)
        )
        salaries_table.append(
            (language, stat['vacancies_found'], stat['vacancies_processed'], stat['average_salary'])
        )

    table = AsciiTable(salaries_table, 'HeadHunter Moscow')
    return table.table

def main():
    env = Env()
    env.read_env()
    superjob_secret_key = env.str("SUPERJOB_SECRET_KEY")

    languages = ['Python', 'Java', 'Golang', 'Javascript', 'Ruby', 'PHP', 'C++', '1С']

    print(get_superjob_salaries_table(languages, superjob_secret_key))

    print(get_hh_salaries_table(languages))


if __name__ == '__main__':
    main()
