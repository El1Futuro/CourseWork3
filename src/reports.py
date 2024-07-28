import functools
import json
from typing import Any
from src.utils import logger
import pandas as pd
from dateutil.relativedelta import relativedelta


def save_report_to_file(filename: str = None) -> Any:
    """Декоратор для функции, сохраняет результат в файл my_report.json"""
    def decorator(func: Any) -> Any:
        @functools.wraps(func)
        def wrapper(last_three_months: pd.DataFrame) -> Any:
            logger.info("Вызываем функцию для преобразования данных в формат JSON")
            result = func(last_three_months)
            if filename is not None:
                logger.info("Сохраняем результат в файл my_report.json")
                with open("my_report.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=4, default=str)
            return result

        return wrapper

    return decorator


def spending_by_category(excel_list: pd.DataFrame, search_category: str, user_date_input: str = None) -> Any:
    """Функция фильтрует полученный список согласно полученным параметрам"""
    logger.info("Начинаем фильтрацию транзакций по категории и дате")
    # Если дата не передана, то берется текущая дата
    if user_date_input is None:
        date = pd.Timestamp.now()
    else:
        date = pd.to_datetime(user_date_input, format="%d.%m.%Y")

    logger.info("Выбираем только те транзакции, которые относятся к заданной категории")
    category_transactions = excel_list[excel_list["Категория"].str.lower() == search_category.lower()]
    category_transactions.loc[:, "Дата операции"] = pd.to_datetime(
        category_transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S"
    )

    logger.info("Выбираем только те транзакции, которые были совершены за последние три месяца от переданной даты")
    last_three_months = category_transactions[
        (category_transactions["Дата операции"] >= date - relativedelta(months=3))
        & (category_transactions["Дата операции"] < date)
    ]

    logger.info("Возвращаем сумму трат по заданной категории за последние три месяца")
    amount_spent = last_three_months["Сумма операции"].sum()
    if amount_spent != 0:
        logger.info("Найдены транзакции по заданным параметрам")
        print("Транзакции, которые были совершены за последние три месяца от переданной даты")
        print(f"Сумма транзакций: {amount_spent}")
        return last_three_months

    else:
        logger.info("Транзакций по заданным параметрам не найдено")
        print("По Вашему запросу не найдено ни одной транзакции")
        print(f"Сумма транзакций: {amount_spent}")
        return pd.DataFrame()


@save_report_to_file(filename="my_report.json")
def transaction_xlsx_utils(last_three_months: pd.DataFrame) -> list[dict]:
    """Обрабатывает словарь полученный из file.xlsx и преобразует его в список формата json"""
    logger.info("Начинаем преобразование данных в формат JSON")
    list_transactions = []
    for index, row in last_three_months.iterrows():
        result = {
            "Дата операции": row["Дата операции"].strftime("%Y-%m-%d %H:%M:%S"),
            "Дата платежа": row["Дата платежа"],
            "Номер карты": "" if pd.isna(row["Номер карты"]) else row["Номер карты"],
            "Статус": row["Статус"],
            "Сумма операции": row["Сумма операции"],
            "Валюта операции": row["Валюта операции"],
            "Сумма платежа": row["Сумма платежа"],
            "Валюта платежа": row["Валюта платежа"],
            "Кэшбэк": "" if pd.isna(row["Кэшбэк"]) else row["Кэшбэк"],
            "Категория": "" if pd.isna(row["Категория"]) else row["Категория"],
            "MCC": "" if pd.isna(row["MCC"]) else row["MCC"],
            "Описание": "" if pd.isna(row["Описание"]) else row["Описание"],
            "Бонусы(включая кэшбэк)": row.get("Бонусы(включая кэшбэк)", ""),
            "Округление на инвесткопилку": row.get("Округление на инвесткопилку", ""),
            "Сумма операции с округлением": row.get("Сумма операции с округлением", ""),
        }
        list_transactions.append(result)
    logger.info("Преобразование данных в формат JSON завершено")
    return list_transactions
