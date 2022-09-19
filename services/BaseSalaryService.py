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

    def get_rows_for_salaries_table(self):
        salaries_table = [
            ('Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата')
        ]

        for language in self.languages:
            stat = self.get_average_salary_stat(
                self.get_vacancies_by_language(language)
            )
            salaries_table.append(
                (language, stat['vacancies_found'], stat['vacancies_processed'], stat['average_salary'])
            )

        return salaries_table

    def get_salaries_table(self):
        table = AsciiTable(self.get_rows_for_salaries_table(), self.title)
        return table.table
