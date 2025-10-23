from functools import wraps
from time import time
from typing import Any, Callable, Optional, TypeVar

T = TypeVar("T")


def log(filename: Optional[str] = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            result: Optional[T] = None
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
                        with open(filename, "a", encoding="utf-8") as f:
                            f.write(log_text)
                    else:
                        print(log_text, end="")

            # Гарантируем, что result не None при успешном выполнении
            if result is None:
                raise RuntimeError("Function completed successfully but returned None")
            return result

        return wrapper

    return decorator
