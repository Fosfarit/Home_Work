import pytest

from src.widget import get_date, mask_account_card


@pytest.mark.parametrize(
    "number_card, expected",
    [
        ("Visa Platinum 7000792289606361", "Visa Platinum 7000 79** **** 6361"),
        ("Счет 73654108430135874305", "Счет **4305"),
        ("79865456", "Некорректные данные"),
    ],
)
def test_mask_account_card(number_card: str, expected: str) -> None:
    assert mask_account_card(number_card) == expected


def test_get_date(date: str) -> None:
    assert get_date(date) == "11.03.2024"
