# import json
#
# import requests
#
# # Проверка API ключа на истинность и состояние
#
# API_KEY = "ChtfQ2c7h41JlYg8RUipERlWiBF8amna"  # твой API_KEY
# url = "https://api.apilayer.com/exchangerates_data/convert"
#
# headers = {"apikey": API_KEY}
#
# params = {"from": "USD", "to": "RUB", "amount": 100}
#
#
# # Проверим сам API ключ через другой эндпоинт
# def test_api_key():
#     test_url = "https://api.apilayer.com/exchangerates_data/symbols"
#     response = requests.get(test_url, headers=headers)
#     print("API Key Test - Status Code:", response.status_code)
#     if response.status_code == 200:
#         print("API Key is valid")
#         return True
#     else:
#         print("API Key test failed:", response.text)
#         return False
#
#
# if test_api_key():
#     # response = requests.get(url, headers=headers, params=params, timeout=10)
#     print("\nConvert Request - Status Code:", response.status_code)
#     print("Response:", response.json())
# else:
#     print("\nPlease check your API key")
