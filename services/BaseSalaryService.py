from abc import ABC, abstractmethod

from terminaltables import AsciiTable

class BaseSalaryService(ABC):
    def __init__(self, languages, title):
        self.languages = languages
        self.title = title

    @abstractmethod
    def get_vacancies_by_language(self):
        pass

    @abstractmethod
    def predict_rub_salary(self, vacancy):
        pass

    @staticmethod
    def predict_rub_salary_util(salary_from=None, salary_to=None):
        if salary_from and salary_to:
            return int((salary_from + salary_to) / 2)

        if salary_from:
            return int(salary_from * 1.2)

        if salary_to:
            return int(salary_to * 0.8)

        return None

    def get_average_salary_stat(self, vacancies):
        count = 0
        amount = 0

        for vacancy in vacancies['vacancies']:
            salary = self.predict_rub_salary(vacancy)
            if salary:
                count += 1
                amount += int(salary)

        return {
            'average_salary': int(amount / count) if count > 0 else 0,
            'vacancies_processed': count,
            'vacancies_found': vacancies['total']
        }

    def fetch_vacancies(self):
        return [(language, self.get_vacancies_by_language(language)) for language in self.languages]

    def get_rows_for_salaries_table(self, vacancies_stat):
        salaries_table = [
            ('Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата')
        ]

        for (language, vacancy_stat) in vacancies_stat:
            salaries_table.append(
                (
                    language,
                    vacancy_stat['vacancies_found'],
                    vacancy_stat['vacancies_processed'],
                    vacancy_stat['average_salary']
                )
            )

        return salaries_table

    def get_salaries_table(self):
        vacancies = self.fetch_vacancies();
        vacancies_stat = [self.get_average_salary_stat(vacancy) for vacancy in vacancies]

        table = AsciiTable(self.get_rows_for_salaries_table(vacancies_stat), self.title)
        return table.table
