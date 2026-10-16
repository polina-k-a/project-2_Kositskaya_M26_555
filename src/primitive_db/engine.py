"""Запуск, игровой цикл и парсинг команд"""

import shlex

import prompt

from primitive_db.core import OK, create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata

FILE_PATH = "db_meta.json"


def print_help() -> None:
    instructions = (
        "***Процесс работы с таблицей***\n"
        "Функции:\n"
        "<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .."
        " - создать таблицу\n"
        "<command> list_tables - показать список всех таблиц\n"
        "<command> drop_table <имя_таблицы> - удалить таблицу\n"
        "<command> exit - выйти из программы\n"
        "<command> help - справочная информация\n"
    )
    print(instructions)


def run() -> None:
    print_help()
    while True:
        metadata = load_metadata(FILE_PATH)
        user_input = prompt.string("\n>>>Введите команду: ")
        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue
        command = args[0] if args else ""
        match command:
            case "create_table":
                if len(args) < 3:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                metadata, status = create_table(metadata, args[1], args[2:])
                if status == OK:
                    save_metadata(FILE_PATH, metadata)
            case "list_tables":
                if len(args) != 1:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                list_tables(metadata)
            case "drop_table":
                if len(args) != 2:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                metadata, status = drop_table(metadata, args[1])
                if status == OK:
                    save_metadata(FILE_PATH, metadata)
            case "help":
                if len(args) != 1:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                print_help()
            case "exit":
                if len(args) != 1:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                print("Выход из программы...")
                break
            case _:
                print(f"Функции {command} нет. Попробуйте снова.")
