from src.masks import get_mask_account, get_mask_card_number

card_number = "7000792289606361"
number_account = "73654108430135874305"

print(get_mask_card_number(card_number))
print(get_mask_account(number_account))
