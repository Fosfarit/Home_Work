def get_mask_card_number(number_card: str) -> str:
    """Функция принимает на вход номер карты и возвращает ее маску"""
    if len(number_card) == 16 and number_card.isdigit():
        return f"{number_card[:4]} {number_card[4:6]}** **** {number_card[-4:]}"
    else:
        return f"Некорректные данные карты"


def get_mask_account(number_account: str) -> str:
    """Функция принимает на вход номер счета и возвращает его маску"""
    if len(number_account) == 20 and number_account.isdigit():
        return f"**{number_account[-4:]}"
    else:
        return f"Некорректные данные счета"
