"""Декораторы для операций с базой данных."""

import time
from functools import wraps
from typing import Any, Callable

from primitive_db.constants import (
    DATABASE_ERR,
    FILE_NOT_FOUND_ERR,
)


def handle_db_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """Обрабатывает исключения при работе с базой данных."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
            return None, FILE_NOT_FOUND_ERR
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")

        return None, DATABASE_ERR

    return wrapper


def confirm_action(action_name: str) -> Callable[..., Any]:
    """Запрашивает подтверждение перед опасной операцией."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            answer = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return None, DATABASE_ERR

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """Измеряет время выполнения функции."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - start
            print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд")

    return wrapper


def create_cacher() -> tuple[
    Callable[[str, Callable[[], Any]], Any],
    Callable[[], None],
]:
    """Создает замыкание для кэширования результатов."""

    cache: dict[str, Any] = {}

    def cache_result(key: str, value_func: Callable[[], Any]) -> Any:
        if key in cache:
            return cache[key]

        result = value_func()
        cache[key] = result
        return result

    def clear_cache() -> None:
        cache.clear()

    return cache_result, clear_cache
