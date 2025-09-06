from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(card: str) -> str:
    """Функция для обработки информации о картах и счетах"""
    list_card = card.split(" ")
    if len(list_card[-1]) == 16 and list_card[-1].isdigit():
        return f"{" ".join(list_card[:-1])} {get_mask_card_number(list_card[-1])}"
    elif len(list_card[-1]) == 20 and list_card[-1].isdigit():
        return f"{" ".join(list_card[:-1])} {get_mask_account(list_card[-1])}"
    else:
        return "Некорректные данные"


def get_date(date: str) -> str:
    """Функция обработки даты"""
    list_date = date.split("T")
    list_date_split = list_date[0].split("-")
    return ".".join(list_date_split[::-1])
