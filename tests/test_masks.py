from src.masks import get_mask_account, get_mask_card_number


def test_get_mask_card_number(number_card: str) -> None:
    assert get_mask_card_number(number_card) == "7000 79** **** 6361"
    assert get_mask_card_number("135415665565656651") == "Некорректный номер карты"


def test_get_mask_account(number_account: str) -> None:
    assert get_mask_account(number_account) == "**4305"
    assert get_mask_account("13541561") == "**1561"
