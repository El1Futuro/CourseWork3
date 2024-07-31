import pandas as pd

from src.utils import logger


def transactions_by_user_choice(search_string: str, excel_list: list) -> list[dict]:
    """Функция фильтрует полученный список по введенному пользователем слову для поиска"""

    excel_list = pd.DataFrame(excel_list).to_dict(orient="records")
    if not excel_list:
        return []

    filtered_list = [
        dicts
        for dicts in excel_list
        if (isinstance(dicts.get("Описание"), str) and search_string.lower() in dicts.get("Описание", "").lower())
        or (
            isinstance(dicts.get("Категория"), str) and search_string.lower() in dicts.get("Категория", "").lower()
        )
    ]
    logger.info(f"Найдено {len(filtered_list)} транзакций по запросу '{search_string}'")
    if filtered_list:
        return filtered_list
    else:
        logger.warning(f"Не найдено ни одной транзакции по запросу '{search_string}'")
        return []
