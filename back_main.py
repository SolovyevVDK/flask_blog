import json
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from functions import auth, all_write, logout, clean_base, path_to_txt, read_category_price, read_products_id, \
    read_stocks, read_suppliers, read_category, read_products_name, category_pricelist, timedata, invoice_by_number, \
    all_invoices
from variables import protocol, server, port, bd
import hashlib

login = 'admin'  # Со страницы авторизации
password = 'restoRtest'  # Со страницы авторизации
token = auth(login, password)  # Функция получения токена, написана в файле

print(token.text)
logout(token)
