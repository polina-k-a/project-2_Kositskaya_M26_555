"""Основная логика работы с таблицами и данными"""

import json
import re

from primitive_db.constants import (
    DUPLICATE_COLUMN_ERR,
    INVALID_COLUMN_ERR,
    INVALID_TABLE_NAME_ERR,
    INVALID_TYPE_ERR,
    INVALID_VALUES_COUNT_ERR,
    OK,
    RECORD_NOT_FOUND_ERR,
    TABLE_EXISTS_ERR,
    TABLE_NOT_FOUND_ERR,
)
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)

ALLOWED_TYPES = {"int", "str", "bool"}
TYPE_CONVERTERS = {
    "int": int,
    "str": str,
    "bool": lambda value: value.lower() == "true",
}

cache_result, clear_cache = create_cacher()


@handle_db_errors
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
        return metadata, INVALID_TABLE_NAME_ERR
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata, TABLE_EXISTS_ERR
    id_specified = False
    # Добавляем ID:int в начало метаданных таблицы
    table_columns = {"ID": "int"}
    # Проверяем корректность типов данных
    for column in columns:
        if column.count(":") != 1:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata, INVALID_COLUMN_ERR
        col_name, col_type = column.split(":")
        if col_type not in ALLOWED_TYPES:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata, INVALID_TYPE_ERR
        if not re.fullmatch(r"[A-Za-z0-9_]+", col_name):
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata, INVALID_COLUMN_ERR
        if col_name == "ID":
            if col_type != "int" or id_specified:
                print(f"Некорректное значение: {column}. Попробуйте снова.")
                return metadata, INVALID_COLUMN_ERR
            id_specified = True
            continue
        if col_name in table_columns:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata, DUPLICATE_COLUMN_ERR
        table_columns[col_name] = col_type

    # Обновляем словарь metadata
    metadata[table_name] = table_columns
    print(
        f'Таблица "{table_name}" успешно создана со столбцами: '
        + ", ".join(f"{k}:{v}" for k, v in table_columns.items())
    )
    return metadata, OK


@handle_db_errors
@confirm_action("удаление таблицы")
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
        return metadata, TABLE_NOT_FOUND_ERR
    del metadata[table_name]
    clear_cache()
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


@handle_db_errors
@log_time
def insert(
    metadata: dict[str, dict[str, str]],
    table_name: str,
    table_data: list[dict[str, str | int | bool]] | None,
    values: list[str],
) -> tuple[list[dict[str, str | int | bool]] | None, int]:
    """
    Функция для вставки новой записи в таблицу. Проверяет:
    существует ли таблица,
    что количество переданных значений соответствует количеству столбцов (минус ID).
    Валидирует типы данных для каждого значения в соответствии со схемой в metadata.
    Генерирует новый ID (например, max(IDs) + 1 или len(data) + 1).
    Добавляет новую запись (в виде словаря) в данные таблицы и возвращает их.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data, TABLE_NOT_FOUND_ERR
    if len(values) != len(metadata[table_name]) - 1:
        print(
            f"Ошибка: Количество переданных значений не соответствует количеству "
            f"столбцов в таблице {table_name}. Попробуйте снова."
        )
        return table_data, INVALID_VALUES_COUNT_ERR
    metadata_table = list(metadata[table_name].values())[1:]
    for value, expected_type in zip(values, metadata_table):
        if expected_type == "int":
            if '"' in value or not value.lstrip("-").isdigit():
                print(
                    f"Ошибка: Значение '{value}' не соответствует типу 'int'. "
                    "Попробуйте снова."
                )
                return table_data, INVALID_TYPE_ERR
        elif expected_type == "bool":
            if '"' in value or value.lower() not in {"true", "false"}:
                print(
                    f"Ошибка: Значение '{value}' не соответствует типу 'bool'. "
                    "Попробуйте снова."
                )
                return table_data, INVALID_TYPE_ERR
        elif expected_type == "str":
            if len(value) < 2 or not (value[0] == '"' and value[-1] == '"'):
                print(f"Ошибка: Значение '{value}' не соответствует типу 'str'.")
                return table_data, INVALID_TYPE_ERR
    if table_data is None:
        table_data = []
    new_id = max((row["ID"] for row in table_data), default=0) + 1
    converted_values = [
        value[1:-1] if expected_type == "str" else value
        for value, expected_type in zip(values, metadata_table)
    ]
    table_data.append(
        {
            column: TYPE_CONVERTERS[expected_type](v)
            for column, expected_type, v in zip(
                metadata[table_name].keys(),
                metadata[table_name].values(),
                [str(new_id)] + converted_values,
            )
        }
    )
    clear_cache()
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data, OK


@handle_db_errors
@log_time
def select(
    table_data: list[dict[str, str | int | bool]],
    where_clause: dict[str, str | int | bool] | None = None,
) -> tuple[list[dict[str, str | int | bool]], int]:
    """
    Функция получения данных таблицы с фильтром.
    Кэширует результаты одинаковых запросов.
    """

    def get_selected_data() -> list[dict[str, str | int | bool]]:
        if where_clause is None:
            return [row.copy() for row in table_data]

        return [
            row.copy()
            for row in table_data
            if all(row.get(c) == v for c, v in where_clause.items())
        ]

    key = json.dumps(
        {"data": table_data, "where": where_clause},
        sort_keys=True,
        ensure_ascii=False,
    )

    selected_data = cache_result(key, get_selected_data)

    if not selected_data:
        print("Подходящие записи не найдены.")
        return selected_data, RECORD_NOT_FOUND_ERR

    return selected_data, OK


@handle_db_errors
def update(
    table_data: list[dict[str, str | int | bool]],
    set_clause: dict[str, str | int | bool],
    where_clause: dict[str, str | int | bool],
) -> tuple[list[dict[str, str | int | bool]], int]:
    """
    Функция для обновления данных.
    Находит записи по where_clause.
    Обновляет в найденных записях поля согласно set_clause.
    Возвращает измененные данные.
    """
    updated_data = []
    found = False
    for row in table_data:
        if all(row.get(c) == v for c, v in where_clause.items()):
            updated_data.append({**row, **set_clause})
            found = True
        else:
            updated_data.append(row.copy())
    if not found:
        print("Записи, соответствующие условию, не найдены.")
        return updated_data, RECORD_NOT_FOUND_ERR
    clear_cache()
    return updated_data, OK


@handle_db_errors
@confirm_action("удаление записей")
def delete(
    table_data: list[dict[str, str | int | bool]],
    where_clause: dict[str, str | int | bool] | None = None,
) -> tuple[list[dict[str, str | int | bool]], int]:
    """
    Функция находит записи по where_clause и удаляет их.
    Возвращает измененные данные.
    """
    if where_clause is None:
        clear_cache()
        return [], OK
    found = False
    updated_data = []
    for row in table_data:
        if all(row.get(c) == v for c, v in where_clause.items()):
            found = True
        else:
            updated_data.append(row.copy())
    if not found:
        print("Записи, соответствующие условию, не найдены.")
        return updated_data, RECORD_NOT_FOUND_ERR
    clear_cache()
    return updated_data, OK


def info(
    metadata: dict[str, dict[str, str]],
    table_name: str,
    table_data: list[dict[str, str | int | bool]] | None,
) -> None:
    """
    Выводит информацию о таблице.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return
    print(
        f"Таблица: {table_name}\n"
        f"Столбцы: {', '.join(f'{c}:{v}' for c, v in metadata[table_name].items())}\n"
        f"Количество записей: {0 if table_data is None else len(table_data)}"
    )
