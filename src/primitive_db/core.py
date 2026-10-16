"""Основная логика работы с таблицами и данными"""

import re

ALLOWED_TYPES = {"int", "str", "bool"}
OK = 0
ERR = 1


def create_table(
    metadata: dict[str, dict[str, str]], table_name: str, columns: list[str]
) -> tuple[dict[str, dict[str, str]], int]:
    """
    Функция для создания таблицы.
    Принимает текущие метаданные, имя таблицы и список столбцов.
    Проверяет корректность имени таблицы и столбцов, корректность типов данных,
    наличие уже существующей таблицы с таким именем,
    а также наличие повторяющихся столбцов.
    Если все проверки пройдены успешно, обновляет словарь metadata.
    Возвращает кортеж из метаданных и кода результата (OK или ERR).
    """
    if not re.fullmatch(r"[A-Za-z0-9_]+", table_name):
        print(f"Некорректное значение: {table_name}. Попробуйте снова.")
        return metadata, ERR
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata, ERR
    id_specified = False
    # Добавляем ID:int в начало метаданных таблицы
    table_columns = {"ID": "int"}
    # Проверяем корректность типов данных
    for column in columns:
        if column.count(":") != 1:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata, ERR
        col_name, col_type = column.split(":")
        if col_type not in ALLOWED_TYPES:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata, ERR
        if not re.fullmatch(r"[A-Za-z0-9_]+", col_name):
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata, ERR
        if col_name == "ID":
            if col_type != "int" or id_specified:
                print(f"Некорректное значение: {column}. Попробуйте снова.")
                return metadata, ERR
            id_specified = True
            continue
        if col_name in table_columns:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata, ERR
        table_columns[col_name] = col_type

    # Обновляем словарь metadata
    metadata[table_name] = table_columns
    print(
        f'Таблица "{table_name}" успешно создана со столбцами: '
        + ", ".join(f"{k}:{v}" for k, v in table_columns.items())
    )
    return metadata, OK


def drop_table(
    metadata: dict[str, dict[str, str]], table_name: str
) -> tuple[dict[str, dict[str, str]], int]:
    """
    Функция для удаления таблицы.
    Проверяет существование таблицы. Если таблицы нет, выводит ошибку.
    Удаляет информацию о таблице из metadata.
    Возвращает кортеж из метаданных и кода результата (OK или ERR).
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata, ERR
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata, OK


def list_tables(metadata: dict[str, dict[str, str]]) -> None:
    """
    Функция для отображения списка всех таблиц.
    Если таблиц нет, выводит соответствующее сообщение.
    """
    if not metadata:
        print("База данных пуста. Таблицы отсутствуют.")
        return
    for table_name in metadata:
        print(f"- {table_name}")
