import pytest

from src.services import transactions_by_user_choice


@pytest.fixture
def excel_data() -> list:
    return [
        {"Описание": "Покупка продуктов", "Категория": "Продукты питания", "Сумма": 100},
        {"Описание": "Покупка одежды", "Категория": "Одежда", "Сумма": 200},
    ]


def test_transactions_by_user_choice_empty_list():
    result = transactions_by_user_choice("продукты", [])
    assert result == []


def test_transactions_by_user_choice_description(excel_data):
    result = transactions_by_user_choice("продуктов", excel_data)
    assert len(result) == 1
    assert result[0]["Описание"] == "Покупка продуктов"


def test_transactions_by_user_choice_category(excel_data):
    result = transactions_by_user_choice("одежда", excel_data)
    assert len(result) == 1
    assert result[0]["Категория"] == "Одежда"


def test_transactions_by_user_choice_description_and_category(excel_data):
    result = transactions_by_user_choice("покупка одежды", excel_data)
    assert len(result) == 1
    assert result[0]["Описание"] == "Покупка одежды"
    assert result[0]["Категория"] == "Одежда"


def test_transactions_by_user_choice_case_insensitive(excel_data):
    result = transactions_by_user_choice("ПРОДУКТЫ", excel_data)
    assert len(result) == 1
    assert result[0]["Описание"] == "Покупка продуктов"


def test_transactions_by_user_choice_not_found(excel_data):
    result = transactions_by_user_choice("автомобиль", excel_data)
    assert len(result) == 0
