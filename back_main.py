import json
from datetime import datetime, timedelta

import requests

from functions import auth, all_write, logout, clean_base, path_to_txt, read_category_price, read_products_id, read_stocks, read_suppliers, read_category, read_products_name, category_pricelist, timedata
from variables import protocol, server, port, bd
import hashlib

login = 'admin'  # Со страницы авторизации
password = 'restoRtest'  # Со страницы авторизации
# token = auth(login=login, password=password)  # Функция получения токена, написана в файле -
# print(f'{protocol}://{server}:{port}{bd}/api/logout?key={token.text}')
# print(token)
# #
# #
# all_write(token)
# #
# logout(token)

url = f'http://193.124.64.147:8084/resto/auth?login={login}&pass={hashlib.sha1(password.encode("utf-8")).hexdigest()}'
test = requests.get(url)
print(test.text)


