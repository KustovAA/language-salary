import requests
from environs import Env
from terminaltables import AsciiTable


def predict_rub_salary_util(salary_from=None, salary_to=None):
    if salary_from and salary_to:
        return int((salary_from + salary_to) / 2)

    if salary_from:
        return int(salary_from * 1.2)

    if salary_to:
        return int(salary_to * 0.8)

    return None


def predict_rub_salary_hh(vacancy):
    salary = vacancy["salary"]

    if salary["currency"] != "RUR":
        return None

    return predict_rub_salary_util(salary["from"], salary["to"])


def predict_rub_salary_sj(vacancy):
    return predict_rub_salary_util(vacancy["payment_from"], vacancy["payment_to"])


def get_vacancies_by_language_hh(language):
    url = "https://api.hh.ru/vacancies"
    moscow_area_id = 1
    params = {
        "text": language,
        "area": moscow_area_id,
        "only_with_salary": True,
        "per_page": 100,
    }

    has_next = True
    vacancies = []
    page = 0
    total = 0

    while has_next:
        params["page"] = page
        response = requests.get(url, params=params)
        response.raise_for_status()
        vacancies_search_result = response.json()

        pages = vacancies_search_result["pages"]
        vacancies += vacancies_search_result["items"]
        total = vacancies_search_result["found"]
        page += 1
        has_next = page < pages

    return {"vacancies": vacancies, "total": total}


def get_vacancies_by_language_sj(language, api_key):
    url = "https://api.superjob.ru/2.0/vacancies"
    params = {"town": "Москва", "keyword": language, "count": 100}
    headers = {"X-Api-App-Id": api_key}

    has_next = True
    vacancies = []
    page = 0
    total = 0

    while has_next:
        params["page"] = page
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        vacancies_search_result = response.json()

        more = vacancies_search_result["more"]
        vacancies += vacancies_search_result["objects"]
        total = vacancies_search_result["total"]
        page += 1
        has_next = more

    return {"vacancies": vacancies, "total": total}


def get_average_salary_stat(vacancies, predict_rub_salary):
    count = 0
    amount = 0

    for vacancy in vacancies["vacancies"]:
        salary = predict_rub_salary(vacancy)
        if salary:
            count += 1
            amount += int(salary)

    return {
        "average_salary": int(amount / count) if count > 0 else 0,
        "vacancies_processed": count,
        "vacancies_found": vacancies["total"],
    }


def get_rows_for_salaries_table(vacancies_stat):
    salaries_table = [
        (
            "Язык программирования",
            "Вакансий найдено",
            "Вакансий обработано",
            "Средняя зарплата",
        )
    ]

    for (language, vacancy_stat) in vacancies_stat:
        salaries_table.append(
            (
                language,
                vacancy_stat["vacancies_found"],
                vacancy_stat["vacancies_processed"],
                vacancy_stat["average_salary"],
            )
        )

    return salaries_table


def create_salaries_table(table_rows, title):
    table = AsciiTable(table_rows, title)
    return table.table


def main():
    env = Env()
    env.read_env()
    superjob_secret_key = env.str("SUPERJOB_SECRET_KEY")

    languages = ["Python", "Java", "Golang", "Javascript", "Ruby", "PHP", "C++", "1С"]

    vacancies_hh = [
        (language, get_vacancies_by_language_hh(language)) for language in languages
    ]
    salary_stat_hh = [
        (language, get_average_salary_stat(vacancy, predict_rub_salary_hh))
        for (language, vacancy) in vacancies_hh
    ]
    table_rows_hh = get_rows_for_salaries_table(salary_stat_hh)
    salary_table_hh = create_salaries_table(table_rows_hh, "HeadHunter Moscow")
    print(salary_table_hh)

    vacancies_sj = [
        (language, get_vacancies_by_language_sj(language, superjob_secret_key))
        for language in languages
    ]
    salary_stat_sj = [
        (language, get_average_salary_stat(vacancy, predict_rub_salary_sj))
        for (language, vacancy) in vacancies_sj
    ]
    table_rows_sj = get_rows_for_salaries_table(salary_stat_sj)
    salary_table_sj = create_salaries_table(table_rows_sj, "Superjob Moscow")
    print(salary_table_sj)


if __name__ == "__main__":
    main()
