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
    MOSCOW_AREA_ID = 1
    params = {
        'text': language,
        'area': MOSCOW_AREA_ID,
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
        data = response.json()

        pages = data['pages']
        vacancies += data['items']
        total = data['found']
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
        data = response.json()

        more = data['more']
        vacancies += data['objects']
        total = data['total']
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


def print_salary_info_superjob(languages, api_key):
    table_data = [
        ('Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата')
    ]

    for language in languages:
        stat = get_average_salary_stat_superjob(
            get_vacancies_by_language_superjob(language, api_key=api_key)
        )
        table_data.append(
            (language, stat['vacancies_found'], stat['vacancies_processed'], stat['average_salary'])
        )

    table = AsciiTable(table_data, 'SuperJob Moscow')
    print(table.table)


def print_salary_info_hh(languages):
    table_data = [
        ('Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата')
    ]

    for language in languages:
        stat = get_average_salary_stat_hh(
            get_vacancies_by_language_hh(language)
        )
        table_data.append(
            (language, stat['vacancies_found'], stat['vacancies_processed'], stat['average_salary'])
        )

    table = AsciiTable(table_data, 'HeadHunter Moscow')
    print(table.table)

def main():
    env = Env()
    env.read_env()
    superjob_secret_key = env.str("SUPERJOB_SECRET_KEY")

    languages = ['Python', 'Java', 'Golang', 'Javascript', 'Ruby', 'PHP', 'C++', '1С']

    print_salary_info_superjob(languages, superjob_secret_key)

    print_salary_info_hh(languages)


if __name__ == '__main__':
    main()
