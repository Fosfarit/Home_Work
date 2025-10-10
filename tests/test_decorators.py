from _pytest.capture import CaptureFixture

from src.decorators import log


@log()
def func_div(a: float, b: float) -> float:
    return a / b


def test_log_console_success(capsys: CaptureFixture) -> None:
    """Тест логирования успешного выполнения в консоль"""
    func_div(4, 2)
    captured = capsys.readouterr()
    assert "func_div ok." in captured.out
    assert "Time:" in captured.out
    assert "s\n" in captured.out


def test_log_console_error(capsys: CaptureFixture) -> None:
    """Тест логирования ошибки в консоль"""
    try:
        func_div(4, 0)
    except ZeroDivisionError:
        pass

    captured = capsys.readouterr()
    assert "func_div error: ZeroDivisionError" in captured.out
    assert "Inputs: (4, 0)" in captured.out
    assert "{}\n" in captured.out


def test_log_preserves_function_behavior() -> None:
    """Тест, что декоратор не ломает основную функциональность функции"""

    @log()
    def add(a: int, b: int) -> int:
        return a + b

    result = add(2, 3)
    assert result == 5
