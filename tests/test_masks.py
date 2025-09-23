from src.masks import get_mask_account, get_mask_card_number


def test_get_mask_card_number(number_card: str) -> None:
    assert get_mask_card_number(number_card) == "7000 79** **** 6361"
    assert get_mask_card_number("546468646") == "Номер карты должен быть 16 цифр"


def test_get_mask_account(number_account: str) -> None:
    assert get_mask_account(number_account) == "**4305"
    assert get_mask_card_number("5565647") == "Номер карты должен быть не меннее 4 цифр"
