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
# print(invoice_by_number(token, '0005'))
suppliers = read_suppliers()
invoices_number_list = []
invoices_date_list = []
invoices_counteragentId_list = []
for name, id in suppliers.items():
    invoices = all_invoices(token, supid=id)
    soup = BeautifulSoup(invoices, 'xml')
    for num in soup.find_all('documentNumber'):
        invoices_number_list.append(num.text)

    for dateIncoming in soup.find_all('dateIncoming'):
        invoices_date_list.append(dateIncoming.text)

    for counteragentId in soup.find_all('counteragentId'):
        invoices_counteragentId_list.append(counteragentId.text)

print(invoices_number_list)
logout(token)
