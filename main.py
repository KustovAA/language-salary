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


def predict_rub_salary(vacancy, settings):
    match settings["strategy"]:
        case "hh":
            salary = vacancy["salary"]

            if salary["currency"] != "RUR":
                return None

            return predict_rub_salary_util(salary["from"], salary["to"])
        case "superjob":
            return predict_rub_salary_util(
                vacancy["payment_from"], vacancy["payment_to"]
            )


def get_vacancies_by_language(language, settings):
    match settings["strategy"]:
        case "hh":
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

        case "superjob":
            url = "https://api.superjob.ru/2.0/vacancies"
            params = {"town": "Москва", "keyword": language, "count": 100}
            headers = {"X-Api-App-Id": settings["api_key"]}

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


def get_average_salary_stat(vacancies, settings):
    count = 0
    amount = 0

    for vacancy in vacancies["vacancies"]:
        salary = predict_rub_salary(vacancy, settings)
        if salary:
            count += 1
            amount += int(salary)

    return {
        "average_salary": int(amount / count) if count > 0 else 0,
        "vacancies_processed": count,
        "vacancies_found": vacancies["total"],
    }


def fetch_vacancies(languages, settings):
    return [
        (language, get_vacancies_by_language(language, settings))
        for language in languages
    ]


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


def get_salary_stat(languages, settings):
    vacancies = fetch_vacancies(languages, settings)

    return [
        (language, get_average_salary_stat(vacancy, settings))
        for (language, vacancy) in vacancies
    ]


def get_salaries_table(salary_stat, title):
    table = AsciiTable(get_rows_for_salaries_table(salary_stat), title)
    return table.table


def main():
    env = Env()
    env.read_env()
    superjob_secret_key = env.str("SUPERJOB_SECRET_KEY")

    languages = ["Python", "Java", "Golang", "Javascript", "Ruby", "PHP", "C++", "1С"]

    salary_stat_hh = get_salary_stat(languages, {"strategy": "hh"})
    print(get_salaries_table(salary_stat_hh, "HeadHunter Moscow"))

    salary_stat_superjob = get_salary_stat(
        languages,
        {
            "api_key": superjob_secret_key,
            "strategy": "superjob",
        },
    )
    print(get_salaries_table(salary_stat_superjob, "SuperJob Moscow"))


if __name__ == "__main__":
    main()
