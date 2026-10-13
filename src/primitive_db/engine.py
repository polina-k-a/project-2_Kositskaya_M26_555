import prompt


def welcome() -> None:
    instructions = (
        "\n<command> exit - выйти из программы\n"
        "<command> help - справочная информация\n"
        "Введите команду: "
    )
    command = ""

    print("Первая попытка запустить проект! \n\n***")
    while command != "exit":
        command = prompt.string(instructions)
        match command:
            case "help":
                pass
            case "exit":
                print("Выход из программы...")
            case _:
                print(f"Неизвестная команда: {command}. Введите 'help' для справки.")
