import json


def load_metadata(filepath: str) -> dict[str, dict[str, str]]:
    """
    Загружает данные из JSON-файла.
    Если файл не найден, возвращает пустой словарь {}
    """
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, metadata: dict[str, dict[str, str]]) -> None:
    """
    Сохраняет переданные данные в JSON-файл.
    """
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False)


def load_table_data(table_name: str) -> list[dict[str, str | int | bool]]:
    """
    Загружает данные таблицы из JSON-файла.
    Если файл не найден, возвращает пустой список []
    """
    try:
        with open(f"data/{table_name}.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list[dict[str, str | int | bool]]) -> None:
    """
    Сохраняет переданные данные таблицы в JSON-файл.
    """
    with open(f"data/{table_name}.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)
