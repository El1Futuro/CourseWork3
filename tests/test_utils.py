import json
import unittest
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd

from src.utils import (get_currency_rates, get_five_transactions_in_dict, get_greeting_by_datetime, get_request_period,
                       get_tickers, get_transactions_excel, get_transactions_in_period, get_user_currencies)


class TestUtils(unittest.TestCase):

    @patch("pandas.read_excel")
    def test_get_transactions_excel(self, mock_read_excel):
        mock_df = pd.DataFrame({"Дата операции": ["2019-02-23 12:00:00"], "Сумма операции": [100]})
        mock_read_excel.return_value = mock_df

        result = get_transactions_excel("excel_file_path")
        self.assertTrue(result.equals(mock_df))

    def test_get_greeting_by_datetime(self):
        result = get_greeting_by_datetime("2023-10-01 19:00:00")
        self.assertEqual(result, {"greeting": "Добрый вечер"})

    def test_get_transactions_in_period(self):
        test_df = pd.DataFrame(
            {"Дата операции": ["23.02.2019 12:00:00", "24.02.2019 12:00:00"], "Сумма операции": [100, 200]}
        )
        result = get_transactions_in_period("23.02.2019", test_df)
        expected_result = pd.DataFrame({"Дата операции": ["23.02.2019 12:00:00"], "Сумма операции": [100]})
        expected_result["Дата операции"] = pd.to_datetime(expected_result["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        self.assertTrue(result.equals(expected_result))

    @patch("builtins.input", return_value="23.02.2019")
    def test_get_request_period(self, mock_ctypes):
        result = get_request_period()
        self.assertEqual(result, pd.to_datetime("23.02.2019", format="%d.%m.%Y"))

    def test_get_five_transactions_in_dict(self):
        transactions = [
            {
                "Дата операции": pd.Timestamp("2019-02-23"),
                "Сумма операции": 100,
                "Категория": "Еда",
                "Описание": "Рис",
            },
            {
                "Дата операции": pd.Timestamp("2019-02-24"),
                "Сумма операции": 200,
                "Категория": "Транспорт",
                "Описание": "Метро",
            },
        ]
        result = get_five_transactions_in_dict(transactions)
        expected_result = {
            "top_transactions": [
                {"date": "23.02.2019", "amount": 100, "category": "Еда", "description": "Рис"},
                {"date": "24.02.2019", "amount": 200, "category": "Транспорт", "description": "Метро"},
            ]
        }
        self.assertEqual(result, expected_result)

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"user_currencies": ["USD", "EUR"]}))
    def test_get_user_currencies(self, mock_ctypes):
        result = get_user_currencies("json_file_path")
        self.assertEqual(result, ["USD", "EUR"])

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"user_stocks": ["AAPL", "MSFT"]}))
    def test_get_tickers(self, mock_ctypes):
        result = get_tickers("json_file_path")
        self.assertEqual(result, ["AAPL", "MSFT"])

    @patch("requests.get")
    def test_get_currency_rates(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"rates": {"RUB": 75}}
        mock_get.return_value = mock_response

        result = get_currency_rates(["USD"])
        expected_result = {"currency_rates": [{"currency": "USD", "rate": 75}]}
        self.assertEqual(result, expected_result)
