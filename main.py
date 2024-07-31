import json
from typing import Any

from src.reports import spending_by_category, transaction_xlsx_utils
from src.services import transactions_by_user_choice
from src.utils import excel_file_path, get_greeting_by_datetime, get_request_period, get_transactions_excel, logger
from src.views import date_time_str, get_final_report


def main() -> Any:
    """Функция для запуска всего проекта"""
    # Главная страница
    print("\nГЛАВНАЯ\n")

    logger.info("Выводим приветствие в зависимости от времени суток пользователя")
    # Текущее время в формате YYYY-MM-DD HH:MM:SS
    print(get_greeting_by_datetime(date_time_str))
    # Получаем итоговый отчет
    print(get_final_report())

    # Страница сервиса
    print("\nСЕРВИСЫ\n")
    search_string = input("Введите слово для поиска: ")
    result_sort = json.dumps(
        transactions_by_user_choice(search_string, get_transactions_excel(excel_file_path)),
        indent=4,
        ensure_ascii=False,
    )

    if not result_sort:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации.")
    else:
        print(f"Всего банковских операций в выборке: {len(json.loads(result_sort))}")
        print("Распечатываю итоговый список транзакций...")

    print(result_sort)

    # Страница отчета
    print("\nОТЧЕТЫ\n")
    search_category = input("Введите наименование категории для фильтрации: ")
    spending_by_category_result = spending_by_category(
        get_transactions_excel(excel_file_path), search_category, get_request_period()
    )
    print(f"Данные переданы в файл: {"my_report.json"}")
    transaction_list = transaction_xlsx_utils(spending_by_category_result)
    with open("my_report.json", "w", encoding="utf-8") as f:
        json.dump(transaction_list, f, ensure_ascii=False, indent=4, default=str)


if __name__ == "__main__":
    main()
