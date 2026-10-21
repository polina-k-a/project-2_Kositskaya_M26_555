import json

from primitive_db.decorators import handle_db_errors

OK = 0


@handle_db_errors
def load_metadata(filepath: str) -> tuple[dict[str, dict[str, str]] | None, int]:
    """
    Загружает данные из JSON-файла.
    Если файл не найден, возвращает None
    """
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file), OK


@handle_db_errors
def save_metadata(
    filepath: str, metadata: dict[str, dict[str, str]]
) -> tuple[None, int]:
    """
    Сохраняет переданные данные в JSON-файл.
    """
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False)

    return None, OK


@handle_db_errors
def load_table_data(
    table_name: str,
) -> tuple[list[dict[str, str | int | bool]] | None, int]:
    """
    Загружает данные таблицы из JSON-файла.
    Если файл не найден, возвращает None
    """
    with open(f"data/{table_name}.json", "r", encoding="utf-8") as file:
        return json.load(file), OK


@handle_db_errors
def save_table_data(
    table_name: str,
    data: list[dict[str, str | int | bool]],
) -> tuple[None, int]:
    """
    Сохраняет переданные данные таблицы в JSON-файл.
    """
    with open(f"data/{table_name}.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)

    return None, OK
