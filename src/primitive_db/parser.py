from primitive_db.constants import (
    INVALID_CONDITION_ERR,
    INVALID_VALUE_ERR,
    OK,
)


def parse_insert_values(raw_values: str) -> tuple[list[str] | None, int]:
    """Разбирает значения в скобках и проверяет корректность их записи."""
    raw_values = raw_values.strip()

    if raw_values == "" or raw_values[0] != "(" or raw_values[-1] != ")":
        return None, INVALID_VALUE_ERR

    content = raw_values[1:-1]
    values: list[str] = []
    current = ""
    in_quotes = False

    for char in content:
        if char == '"':
            in_quotes = not in_quotes
            current += char
        elif char == "," and not in_quotes:
            values.append(current.strip())
            current = ""
        else:
            current += char

    if in_quotes:
        return None, INVALID_VALUE_ERR

    values.append(current.strip())

    if any(not value for value in values):
        return None, INVALID_VALUE_ERR

    for value in values:
        if '"' in value:
            if value.count('"') != 2 or value[0] != '"' or value[-1] != '"':
                return None, INVALID_VALUE_ERR

    return values, OK


def parse_where_clause(
    raw_clause: str,
    table_columns: dict[str, str],
) -> tuple[dict[str, str | int | bool] | None, int]:
    """Проверяет условие WHERE и преобразует значение к типу столбца."""
    parts = raw_clause.split("=", maxsplit=1)

    if len(parts) != 2:
        return None, INVALID_CONDITION_ERR

    column = parts[0].strip()
    value = parts[1].strip()

    if column not in table_columns:
        return None, INVALID_CONDITION_ERR

    expected_type = table_columns[column]

    if expected_type == "int":
        if not value.lstrip("-").isdigit():
            return None, INVALID_CONDITION_ERR
        converted_value = int(value)

    elif expected_type == "bool":
        if value.lower() not in {"true", "false"}:
            return None, INVALID_CONDITION_ERR
        converted_value = value.lower() == "true"

    elif expected_type == "str":
        if (
            len(value) < 2
            or value[0] != '"'
            or value[-1] != '"'
            or value.count('"') != 2
        ):
            return None, INVALID_CONDITION_ERR
        converted_value = value[1:-1]

    else:
        return None, INVALID_CONDITION_ERR

    return {column: converted_value}, OK
