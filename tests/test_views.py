import pandas as pd
import pytest

from src.views import data_cards_in_period


@pytest.fixture
def transactions():
    return pd.DataFrame(
        {"Номер карты": ["6067", "6067", "5690", "5690", "9012"], "Сумма операции": [-100, -200, -300, -400, 0]}
    )


def test_data_cards_in_period_empty():
    result = data_cards_in_period(pd.DataFrame())
    assert result.empty


def test_data_cards_in_period_one_transaction(transactions):
    result = data_cards_in_period(transactions.iloc[:1])
    expected = {"Кэшбэк": {"6067": 1}, "Сумма расходов": {"6067": -100}}
    assert result[0].to_dict() == expected


def test_data_cards_in_period_transactions_one_card(transactions):
    result = data_cards_in_period(transactions.iloc[:2])
    expected = {"Кэшбэк": {"6067": 3}, "Сумма расходов": {"6067": -300}}
    assert result[0].to_dict() == expected


def test_data_cards_in_period_transactions_cards(transactions):
    result = data_cards_in_period(transactions[:4])
    expected = {"Кэшбэк": {"5690": 7, "6067": 3}, "Сумма расходов": {"5690": -700, "6067": -300}}
    assert result[0].to_dict() == expected
