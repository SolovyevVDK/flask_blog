import json

from functions import auth, all_write, logout, read_products_id, read_stocks, read_suppliers, read_category, read_products_name, category_pricelist
from variables import protocol, server, port, bd

# login = 'admin'  # Со страницы авторизации
# password = 'restoRtest'  # Со страницы авторизации
# token = auth(login=login, password=password)  # Функция получения токена, написана в файле -
# print(f'{protocol}://{server}:{port}{bd}/api/logout?key={token.text}')


# all_write(token)
#
# logout(token)

category_pricelist()
# with open('log/pricelist/Скидка 15%_1.json', encoding='utf-8') as file:
#     test = json.load(file)
#
# print(test)
