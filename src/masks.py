import logging

logger = logging.getLogger("masks")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("../logs/masks.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_mask_card_number(card_number: str) -> str:
    """Функция, которая принимает номер карты и возвращает маску номера"""
    try:
        if len(card_number) == 16:
            logger.info(f" Пользователь ввёл номер карты {card_number}")
            return f"{str(card_number)[0:4]} {str(card_number)[4:6]}** **** {str(card_number)[12:]}"
        else:
            logger.warning(f"{card_number} - некорректный номер карты")
            return "Некорректный номер карты"
    except Exception as err:
        logger.setLevel(logging.ERROR)
        logger.error(f"Произошла ошибка {err}")
        return "Ошибка при обработке номера карты"


def get_mask_account(account_number: str) -> str:
    """Функция, которая принимает номер счета и возвращает маску номера"""
    try:
        logger.info(f" Пользователь ввёл номер счета {account_number}")
        if len(account_number) >= 4:
            return f"**{str(account_number)[-4:]}"
        else:
            logger.warning(f"{account_number} - некорректный номер счета")
            return "Некорректный номер счёта"
    except Exception as err:
        logger.setLevel(logging.ERROR)
        logger.error(f"Произошла ошибка {err}")
        return "Ошибка при обработке номера счета"


# card_number = "7000792289606361"
# account_number = "73654108430135874305"
#
# print( get_mask_card_number(card_number))
# print(get_mask_account(account_number))
