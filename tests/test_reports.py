import pandas as pd
import pytest

from src.reports import spending_by_category, transaction_xlsx_utils


@pytest.fixture
def excel_data() -> list:
    return [
        {
            "Дата операции": "01.01.2022 10:00:00",
            "Дата платежа": "01.01.2022",
            "Номер карты": "1234",
            "Статус": "OK",
            "Сумма операции": -100,
            "Валюта операции": "RUB",
            "Сумма платежа": -100,
            "Валюта платежа": "RUB",
            "Кэшбэк": 5,
            "Категория": "Развлечения",
            "MCC": "5812",
            "Описание": "Кинотеатр",
            "Бонусы(включая кэшбэк)": "",
            "Округление на инвесткопилку": "",
            "Сумма операции с округлением": "",
        },
        {
            "Дата операции": "01.02.2022 10:00:00",
            "Дата платежа": "01.02.2022",
            "Номер карты": "1234",
            "Статус": "OK",
            "Сумма операции": -200,
            "Валюта операции": "RUB",
            "Сумма платежа": -200,
            "Валюта платежа": "RUB",
            "Кэшбэк": 10,
            "Категория": "Развлечения",
            "MCC": "5812",
            "Описание": "Театр",
            "Бонусы(включая кэшбэк)": "",
            "Округление на инвесткопилку": "",
            "Сумма операции с округлением": "",
        },
        {
            "Дата операции": "01.03.2022 10:00:00",
            "Дата платежа": "01.03.2022",
            "Номер карты": "1234",
            "Статус": "OK",
            "Сумма операции": -300,
            "Валюта операции": "RUB",
            "Сумма платежа": -300,
            "Валюта платежа": "RUB",
            "Кэшбэк": 15,
            "Категория": "Развлечения",
            "MCC": "5812",
            "Описание": "Концерт",
            "Бонусы(включая кэшбэк)": "",
            "Округление на инвесткопилку": "",
            "Сумма операции с округлением": "",
        },
        {
            "Дата операции": "01.04.2022 10:00:00",
            "Дата платежа": "01.04.2022",
            "Номер карты": "1234",
            "Статус": "OK",
            "Сумма операции": -400,
            "Валюта операции": "RUB",
            "Сумма платежа": -400,
            "Валюта платежа": "RUB",
            "Кэшбэк": 20,
            "Категория": "Развлечения",
            "MCC": "5812",
            "Описание": "Цирк",
            "Бонусы(включая кэшбэк)": "",
            "Округление на инвесткопилку": "",
            "Сумма операции с округлением": "",
        },
    ]


def test_spending_by_category_empty_list() -> None:
    # Пустой список для тестирования
    excel_data: list = []
    excel_list = pd.DataFrame(excel_data)

    # Вызов функции spending_by_category с пустым списком
    result = spending_by_category(excel_list, "продукты", "01.03.2023")

    # Проверка, что результат является пустым DataFrame
    assert result.empty


def test_spending_by_category(excel_data: list) -> None:
    # Преобразуем данные в DataFrame
    excel_list = pd.DataFrame(excel_data)
    excel_list["Дата операции"] = pd.to_datetime(excel_list["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    # Вызываем функцию spending_by_category
    result = spending_by_category(excel_list, "Развлечения", "01.03.2022")

    # Проверяем результат
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert result["Сумма операции"].sum() == -300


def test_transaction_xlsx_utils_empty_list() -> None:
    # Пустой список для тестирования
    excel_data: list = []
    excel_list = pd.DataFrame(excel_data)

    # Вызов функции spending_by_category с пустым списком
    list_transactions = spending_by_category(excel_list, "продукты", "01.03.2023")

    # Проверка, что результат является пустым DataFrame
    assert list_transactions.empty


def test_transaction_xlsx_utils(excel_data: list) -> None:
    # Преобразуем данные в DataFrame
    excel_list = pd.DataFrame(excel_data)

    # Вызываем функцию spending_by_category
    result = spending_by_category(excel_list, "Развлечения", "01.03.2022")

    # Вызываем функцию transaction_xlsx_utils
    json_result = transaction_xlsx_utils(result)

    # Проверяем результат
    assert isinstance(json_result, list)
    assert len(json_result) == 2
    assert json_result[0]["Сумма операции"] == -100
    assert json_result[1]["Сумма операции"] == -200
