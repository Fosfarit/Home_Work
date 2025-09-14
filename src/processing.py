def filter_by_state(transactions: list[dict], state: str = "EXECUTED") -> list[dict]:
    """
    Функция принимает список словарей
    и опционально значение для ключа state (по умолчанию 'EXECUTED').
    Функция возвращает новый список словарей, содержащий только те словари,
    у которых ключ state соответствует указанному значению.
    """
    filter_transtaction = []
    for transaction in transactions:
        if transaction.get("state") == state:
            filter_transtaction.append(transaction)
    return filter_transtaction


def sort_by_date(transactions: list[dict], ascending: bool = True) -> list[dict]:
    """
    Функция, которая принимает список словарей и
    необязательный параметр, задающий порядок сортировки
    (по умолчанию — убывание).
    Функция должна возвращать новый список,
    отсортированный по дате.
    """
    sorted_transactions_date = sorted(transactions, key=lambda x: x["date"], reverse=ascending)
    return sorted_transactions_date
