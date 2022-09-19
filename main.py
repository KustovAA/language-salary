from environs import Env

from services.HHSalaryService import HHSalaryService
from services.SuperjobSalaryService import SuperjobSalaryService

def main():
    env = Env()
    env.read_env()
    superjob_secret_key = env.str("SUPERJOB_SECRET_KEY")

    languages = ['Python', 'Java', 'Golang', 'Javascript', 'Ruby', 'PHP', 'C++', '1С']

    superjobSalaryService = SuperjobSalaryService(languages, 'SuperJob Moscow', superjob_secret_key)
    hhSalaryService = HHSalaryService(languages, 'HeadHunter Moscow')

    print(superjobSalaryService.get_salaries_table())
    print(hhSalaryService.get_salaries_table())


if __name__ == '__main__':
    main()
