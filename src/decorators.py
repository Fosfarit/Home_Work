from functools import wraps
from time import time
from typing import Any, Callable


def log(filename=None) -> Callable:
    def decorator(func):
        """
        Декоратор для логирования выполнения функций.
        Записывает в лог информацию об успешном выполнении функции или об ошибке,
        включая время выполнения и переданные аргументы.
        """

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Функция обертки с логированием
            """
            log_text = ""
            try:
                time_start = time()
                result = func(*args, **kwargs)
                time_end = time()
                log_text = f"{func.__name__} ok. Time: {time_end - time_start:.6f}s\n"
            except Exception as e:
                log_text = f"{func.__name__} error: {type(e).__name__}. Inputs: {args}, {kwargs}\n"
                raise
            finally:
                if log_text:
                    if filename:
                        with open(filename, 'a', encoding='utf-8') as f:
                            f.write(log_text)
                    else:
                        print(log_text, end='')
            return result
        return wrapper
    return decorator
