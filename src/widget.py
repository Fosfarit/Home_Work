from src.masks import get_mask_card_number, get_mask_account


def mask_account_card(card: str) -> str:
    """Функция для обработки информации о картах и счетах"""
    list_card = card.split(" ")
    if len(list_card[-1]) == 16 and list_card[-1].isdigit():
        return f"{" ".join(list_card[:-1])} {get_mask_card_number(list_card[-1])}"
    elif len(list_card[-1]) == 20 and list_card[-1].isdigit():
        return f"{" ".join(list_card[:-1])} {get_mask_account(list_card[-1])}"
    else:
        return f"Некорректные данные"


card = "Счет 3538303347444789550"
print(mask_account_card(card))
