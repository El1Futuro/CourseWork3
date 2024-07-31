import json
import logging
import os
import ssl
import urllib
from datetime import datetime
from typing import Any

import certifi
import pandas as pd
import requests
from pandas import DataFrame

excel_file_path = os.path.join(os.path.dirname(__file__), "..", "data", "operations.xls")


def setup_logger(file_name: Any, log_file: Any) -> Any:
    """Функция настройки логов для модулей"""

    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger(file_name)
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(log_file, mode="w")
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


file_path_1 = os.path.join(os.path.dirname(__file__), "..", "logs", "views.log")
logger = setup_logger("masks", file_path_1)


def get_transactions_excel(excel_file_path: str) -> DataFrame:
    """Функция принимает путь до EXCEL-файла и возвращает данные финансовых транзакций"""
    excel_list = pd.read_excel(excel_file_path)
    logger.info(f"Проверяем, что файл {excel_file_path} не пустой")
    if isinstance(excel_list, pd.DataFrame):
        return excel_list
    else:
        logger.info(f"Пишет информационное сообщение, если файл {excel_file_path} пустой")
        print("File is empty")


user_date_str = "23.02.2019"


def get_greeting_by_datetime(date_time_str: str) -> dict:
    """Возвращает приветствие в зависимости от времени суток."""
    logger.info("Преобразуем строку с текущим временем в объект datetime")
    date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
    hour = date_time.hour
    if 0 <= hour < 6:
        greeting = "Доброй ночи"
    elif 6 <= hour < 12:
        greeting = "Доброе утро"
    elif 12 <= hour < 18:
        greeting = "Добрый день"
    else:
        greeting = "Добрый вечер"

    response = {"greeting": greeting}
    return response


def get_transactions_in_period(user_date_str: str, excel_list: DataFrame) -> DataFrame:
    """Функция находит все транзакции с начала месяца по введенную дату"""
    logger.info(
        "Преобразуем столбец дат из файла в тип данных datetime и сравниваем с данными, введенными пользователем"
    )
    user_date = datetime.strptime(user_date_str, "%d.%m.%Y")
    excel_list["Дата операции"] = pd.to_datetime(excel_list["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    mask = (
        (excel_list["Дата операции"].dt.year == user_date.year)
        & (excel_list["Дата операции"].dt.month == user_date.month)
        & (excel_list["Дата операции"].dt.day <= user_date.day)
    )
    transactions = excel_list[mask]

    if transactions.empty:
        logger.info("Выводим информацию если транзакций по запросу не найдено")
        print("Нет транзакций в указанный период.")
        return pd.DataFrame()
    else:
        logger.info("Выводим результаты поиска транзакций с начала месяца по введенную дату")
        return transactions


transactions_in_period = get_transactions_in_period(user_date_str, get_transactions_excel(excel_file_path))


def get_request_period() -> Any:
    """Получаем у пользователя дату для формирования отчета по транзакциям за определенный период"""
    while True:
        logger.info("Запрашиваем у пользователя ввод даты в определенном формате")
        user_date_input_user = input("Введите дату для формирования отчета в формате 'дд.мм.гггг'.")
        if len(user_date_input_user) != 10:
            logger.error("Неверный формат даты.")
            print("Неверный формат даты. Пожалуйста, попробуйте еще раз")
            continue
        try:
            datetime.strptime(user_date_input_user, "%d.%m.%Y")
            user_date_input: pd.Timestamp = pd.to_datetime(user_date_input_user, format="%d.%m.%Y")
            return user_date_input
        except ValueError:
            logger.error("Неверный формат даты.")
            print("Неверный формат даты. Пожалуйста, попробуйте еще раз")


def get_five_transactions_in_dict(top_transactions_dict: list[dict]) -> dict:
    """Функция записывает полученные ранее данные по отфильтрованным транзакциям в словарь
    для удобства его преобразования в JSON-объект"""
    logger.info("Создаем словарь с результатами")

    top_transactions = []
    for transaction in top_transactions_dict:
        if set(["Дата операции", "Сумма операции", "Категория", "Описание"]).issubset(transaction.keys()):
            top_transactions.append(
                {
                    "date": transaction["Дата операции"].strftime("%d.%m.%Y"),
                    "amount": transaction["Сумма операции"],
                    "category": transaction["Категория"],
                    "description": transaction["Описание"],
                }
            )

    return {"top_transactions": top_transactions}


def get_user_currencies(json_file_path: str) -> Any:
    """Функция получает из файла коды валют для последующего их использования в запросах"""
    with open(json_file_path, "r", encoding="utf-8") as file:
        logger.info("Загружаем данные из файла в переменную settings")
        settings = json.load(file)
        logger.info('Получаем значение по ключу "user_currencies"')
    user_currencies = settings.get("user_currencies")
    return user_currencies


def get_tickers(json_file_path: str) -> Any:
    """Функция получает из файла тикерный символ акций для последующего их использования в запросах"""
    with open(json_file_path, "r", encoding="utf-8") as file:
        logger.info("Загружаем данные из файла в переменную settings")
        settings = json.load(file)

    logger.info('Получаем значение по ключу "user_stocks"')
    tickers = settings.get("user_stocks")
    return tickers


def get_currency_rates(user_currencies: list) -> dict:
    """Функция делает запрос к стороннему API и возвращает курсы валют в нужном формате"""
    logger.info("Делаем запрос в API для получения курсов валют")
    currency_rates = []
    for currency in user_currencies:
        response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{currency}")
        if response.status_code == 200:
            data = response.json()
            currency_rate = {"currency": currency, "rate": data["rates"]["RUB"]}
            currency_rates.append(currency_rate)
        else:
            logger.error(f"Ошибка при получении курса валюты {currency}")
            return {}

    return {"currency_rates": currency_rates}


def get_stock_prices(url: Any, tickers: list[dict]) -> dict:
    """Функция делает запрос к стороннему API и возвращает данные по акциям в нужном формате"""
    logger.info("Делаем запрос в API для получения данных по акциям")
    context = ssl.create_default_context(cafile=certifi.where())

    with urllib.request.urlopen(url, context=context) as response:
        data = response.read().decode("utf-8")
    stock_data = json.loads(data)

    filtered_stock_data = [stock for stock in stock_data if stock["symbol"] in tickers]
    stock_prices = [{"stock": stock["symbol"], "price": stock["price"]} for stock in filtered_stock_data]

    return {"stock_prices": stock_prices}
