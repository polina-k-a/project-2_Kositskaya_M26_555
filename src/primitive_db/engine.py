"""Запуск, игровой цикл и парсинг команд"""

import re
import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.constants import (
    FILE_NOT_FOUND_ERR,
    FILE_PATH,
    OK,
)
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.parser import (
    parse_insert_values,
    parse_where_clause,
)
from primitive_db.utils import (
    delete_table_file,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help() -> None:
    instructions = (
        "***Процесс работы с таблицей***\n"
        "Функции:\n"
        "<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .."
        " - создать таблицу\n"
        "<command> list_tables - показать список всех таблиц\n"
        "<command> drop_table <имя_таблицы> - удалить таблицу\n"
        "<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) "
        "- создать запись.\n"
        "<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать "
        "записи по условию.\n"
        "<command> select from <имя_таблицы> - прочитать все записи.\n"
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where "
        "<столбец_условия> = <значение_условия> - обновить запись.\n"
        "<command> delete from <имя_таблицы> where <столбец> = <значение> - "
        "удалить запись.\n"
        "<command> info <имя_таблицы> - вывести информацию о таблице.\n"
        "<command> exit - выйти из программы\n"
        "<command> help - справочная информация\n"
    )
    print(instructions)


def run() -> None:
    print_help()
    while True:
        metadata, status = load_metadata(FILE_PATH)
        if status == FILE_NOT_FOUND_ERR:
            metadata = {}
        elif status != OK:
            print("Не удалось загрузить метаданные.")
            return
        user_input = prompt.string("\n>>>Введите команду: ").strip()

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        command = args[0] if args else ""

        match command:
            case "create_table":
                handle_create_table(args, user_input, metadata)

            case "list_tables":
                handle_list_tables(args, user_input, metadata)

            case "drop_table":
                handle_drop_table(args, user_input, metadata)

            case "insert":
                handle_insert(user_input, metadata)

            case "select":
                handle_select(user_input, metadata)

            case "update":
                handle_update(user_input, metadata)

            case "delete":
                handle_delete(user_input, metadata)

            case "info":
                handle_info(args, user_input, metadata)

            case "help":
                handle_help(args, user_input)

            case "exit":
                if len(args) != 1:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                print("Выход из программы...")
                break

            case _:
                print(f"Функции {command} нет. Попробуйте снова.")


def handle_create_table(
    args: list[str],
    user_input: str,
    metadata: dict[str, dict[str, str]],
) -> None:
    if len(args) < 3:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return
    metadata, status = create_table(metadata, args[1], args[2:])
    if status == OK:
        _, status = save_metadata(FILE_PATH, metadata)
        if status != OK:
            print("Не удалось сохранить метаданные.")


def handle_list_tables(
    args: list[str],
    user_input: str,
    metadata: dict[str, dict[str, str]],
) -> None:
    if len(args) != 1:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return
    list_tables(metadata)


def handle_drop_table(
    args: list[str],
    user_input: str,
    metadata: dict[str, dict[str, str]],
) -> None:
    if len(args) != 2:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return
    metadata, status = drop_table(metadata, args[1])
    if status != OK:
        return
    _, status = save_metadata(FILE_PATH, metadata)
    if status != OK:
        print("Не удалось сохранить метаданные.")
        return
    _, status = delete_table_file(args[1])
    if status != OK:
        print("Не удалось удалить файл таблицы.")
        return

    print(f'Таблица "{args[1]}" успешно удалена.')


def handle_insert(
    user_input: str,
    metadata: dict[str, dict[str, str]],
) -> None:
    match_insert = re.fullmatch(
        r"insert\s+into\s+([A-Za-z0-9_]+)\s+values\s*(\(.*\))",
        user_input,
    )
    if match_insert is None:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return

    table_name = match_insert.group(1)
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    values, status = parse_insert_values(match_insert.group(2))

    if status != OK or values is None:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return

    table_data, status = load_table_data(table_name)
    if status == FILE_NOT_FOUND_ERR:
        table_data = []
    elif status != OK:
        print(f'Файл с данными таблицы "{table_name}" повреждён')
        return

    updated_data, status = insert(metadata, table_name, table_data, values)

    if status == OK and updated_data is not None:
        _, status = save_table_data(table_name, updated_data)
        if status != OK:
            print("Не удалось сохранить данные таблицы.")
            return


def handle_select(
    user_input: str,
    metadata: dict[str, dict[str, str]],
) -> None:
    match_select = re.fullmatch(
        r"select\s+from\s+([A-Za-z0-9_]+)(?:\s+where\s+(.+))?",
        user_input,
    )

    if match_select is None:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return

    table_name = match_select.group(1)

    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    where_clause = None

    if match_select.group(2) is not None:
        where_clause, status = parse_where_clause(
            match_select.group(2),
            metadata[table_name],
        )

        if status != OK:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            return

    table_data, status = load_table_data(table_name)
    if status == FILE_NOT_FOUND_ERR:
        table_data = []
    elif status != OK:
        print(f'Файл с данными таблицы "{table_name}" повреждён')
        return
    selected_data, status = select(table_data, where_clause)

    if status != OK:
        return

    table = PrettyTable()
    table.field_names = list(metadata[table_name].keys())

    for row in selected_data:
        table.add_row([row[column] for column in table.field_names])

    print(table)


def handle_update(
    user_input: str,
    metadata: dict[str, dict[str, str]],
) -> None:
    match_update = re.fullmatch(
        r"update\s+([A-Za-z0-9_]+)\s+set\s+(.+?)\s+where\s+(.+)",
        user_input,
    )

    if match_update is None:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return

    table_name = match_update.group(1)

    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    set_clause, status = parse_where_clause(
        match_update.group(2),
        metadata[table_name],
    )

    if status != OK or set_clause is None:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return

    if "ID" in set_clause:
        print("Ошибка: Нельзя изменять столбец ID.")
        return

    where_clause, status = parse_where_clause(
        match_update.group(3),
        metadata[table_name],
    )

    if status != OK or where_clause is None:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return

    table_data, status = load_table_data(table_name)
    if status == FILE_NOT_FOUND_ERR:
        table_data = []
    elif status != OK:
        print(f'Файл с данными таблицы "{table_name}" повреждён')
        return

    updated_ids = [
        row["ID"]
        for row in table_data
        if all(row.get(c) == v for c, v in where_clause.items())
    ]

    updated_data, status = update(table_data, set_clause, where_clause)

    if status != OK:
        return

    _, status = save_table_data(table_name, updated_data)
    if status != OK:
        print("Не удалось сохранить данные таблицы.")
        return

    for record_id in updated_ids:
        print(f'Запись с ID={record_id} в таблице "{table_name}" успешно обновлена.')


def handle_delete(
    user_input: str,
    metadata: dict[str, dict[str, str]],
) -> None:
    match_delete = re.fullmatch(
        r"delete\s+from\s+([A-Za-z0-9_]+)(?:\s+where\s+(.+))?",
        user_input,
    )

    if match_delete is None:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return

    table_name = match_delete.group(1)

    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    where_clause = None
    where_clause_text = match_delete.group(2)
    if where_clause_text is not None:
        where_clause, status = parse_where_clause(
            where_clause_text,
            metadata[table_name],
        )

        if status != OK:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            return

    table_data, status = load_table_data(table_name)
    if status == FILE_NOT_FOUND_ERR:
        table_data = []
    elif status != OK:
        print(f'Файл с данными таблицы "{table_name}" повреждён')
        return

    deleted_ids = [
        row["ID"]
        for row in table_data
        if where_clause is None or all(row.get(c) == v for c, v in where_clause.items())
    ]

    deleted_data, status = delete(table_data, where_clause)

    if status != OK:
        return

    _, status = save_table_data(table_name, deleted_data)
    if status != OK:
        print("Не удалось сохранить данные таблицы.")
        return

    if where_clause is None:
        print(f'Данные таблицы "{table_name}" успешно удалены.')
    else:
        for record_id in deleted_ids:
            print(f'Запись с ID={record_id} успешно удалена из таблицы "{table_name}".')


def handle_info(
    args: list[str],
    user_input: str,
    metadata: dict[str, dict[str, str]],
) -> None:
    if len(args) != 2:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return

    table_name = args[1]
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return
    table_data, status = load_table_data(table_name)
    if status == FILE_NOT_FOUND_ERR:
        table_data = []
    elif status != OK:
        print(f'Файл с данными таблицы "{table_name}" повреждён')
        return
    info(metadata, table_name, table_data)


def handle_help(args: list[str], user_input: str) -> None:
    if len(args) != 1:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return
    print_help()
