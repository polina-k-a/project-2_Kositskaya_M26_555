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
