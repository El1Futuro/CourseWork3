import json
import os
from datetime import datetime
from typing import Any

import pandas as pd
from dotenv import load_dotenv

from src.utils import (
    get_currency_rates,
    get_five_transactions_in_dict,
    get_greeting_by_datetime,
    get_stock_prices,
    get_tickers,
    get_user_currencies,
    logger,
    transactions_in_period,
)

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_URL = "https://financialmodelingprep.com/api/v3/stock/list?apikey=YsK1dciHoun7xH1aoiJtDHQNvz5V9A3m"


# Получаем текущую директорию скрипта
current_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(os.path.dirname(__file__), "..", "user_settings.json")


# Текущее время в формате YYYY-MM-DD HH:MM:SS
date_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


logger.info("Выводим приветствие в зависимости от времени суток пользователя")
get_greeting_by_datetime(date_time_str)


def data_cards_in_period(transactions_in_period: Any) -> Any:
    """Функция группирует данные по номерам карт, суммирует расходы и выводим начисленный кэшбэк"""
    logger.info("Фильтруем данные, оставляя только расходы (сумма операции < 0)")
    filtered_data = transactions_in_period[transactions_in_period["Сумма операции"] < 0]
    logger.info("Группируем данные по номерам карт и суммируем расходы")
    grouped_data = filtered_data.groupby("Номер карты")["Сумма операции"].sum()
    logger.info("Вычисляем кэшбэк для каждой суммы расходов")
    cashback = grouped_data.apply(lambda x: -x // 100)
    logger.info("Выводим сумму расходов и кэшбэк по каждой карте")
    result_data_card = pd.concat([grouped_data, cashback], axis=1, keys=["Сумма расходов", "Кэшбэк"])
    return result_data_card, grouped_data, cashback


def get_card_info_in_dict(grouped_data: Any, cashback: Any) -> dict:
    """Функция записывает полученные ранее данные по отфильтрованным транзакциям в словарь
    для удобства его преобразования в JSON-объект"""
    card_info = []
    for card_number, total_spent in zip(grouped_data.index, grouped_data):
        card_info.append(
            {
                "last_digits": str(card_number)[-4:],
                "total_spent": round(float(total_spent), 2),
                "cashback": float(cashback[card_number]),
            }
        )
    return {"cards": card_info}


if transactions_in_period is not None:
    logger.info("Вызываем функцию data_cards_in_period и получаем результаты")
    result_data_card, grouped_data, cashback = data_cards_in_period(transactions_in_period)
    logger.info("Вызываем функцию get_card_info_in_dict и передаем ей результаты")
    get_card_info_in_dict(grouped_data, cashback)


def get_top_five_transactions(transactions_in_period: Any) -> Any:
    """Функция сортирует отфильтрованные ранее по дате данные по абсолютному значению суммы операции и
    возвращает только первые 5 строк"""
    logger.info("Добавляем новый столбец с абсолютным значением суммы операции")
    transactions_in_period["Абсолютная сумма"] = transactions_in_period["Сумма операции"].abs()
    logger.info("Сортируем данные по абсолютному значению суммы операции")
    transactions_by_amount_sorted = transactions_in_period.sort_values(by="Абсолютная сумма", ascending=False)
    logger.info("Возвращаем первые 5 строк")
    return transactions_by_amount_sorted.head(5)


top_five_transactions = get_top_five_transactions(transactions_in_period)

# преобразуем DataFrame в список словарей
top_transactions_dict = top_five_transactions.to_dict(orient="records")

get_five_transactions_in_dict(top_transactions_dict)

get_currency_rates(get_user_currencies(json_file_path))

get_stock_prices(API_URL, get_tickers(json_file_path))


def get_final_report() -> Any:
    """Формирование итогового отчета на основании полученных ранее данных и вывод его в определенном формате"""
    final_report = {}
    final_report.update(get_card_info_in_dict(grouped_data, cashback))
    final_report.update(get_five_transactions_in_dict(top_transactions_dict))
    final_report.update(get_currency_rates(get_user_currencies(json_file_path)))
    final_report.update(get_stock_prices(API_URL, get_tickers(json_file_path)))
    return json.dumps(final_report, indent=4, ensure_ascii=False)


get_final_report()
