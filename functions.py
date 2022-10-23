import datetime
import re
import requests
import hashlib
from bs4 import BeautifulSoup
import xml
import os
import csv
import xml.etree.ElementTree as ET

from lxml import html

from variables import protocol, server, port, bd
from datetime import datetime

datetime_string = str(datetime.now())
date_now = datetime_string[0:-7:]


# Получение токена
def auth(login, password):
    sha1pass = hashlib.sha1(password.encode('utf-8')).hexdigest()
    auth_url = (protocol + '://' + server + ':' + port + bd + '/api/auth?login=' + login + '&pass=' + sha1pass)
    token = requests.get(auth_url)
    return token


# Закрытие токена
def logout(token):
    out_url = (protocol + '://' + server + ':' + port + bd + '/api/logout?key=' + token.text)
    requests.get(out_url)


# Получаем список складов
def get_stocks(token):
    gets_url = (protocol + '://' + server + ':' + port + bd + '/api/corporation/stores?key=' + token.text)
    store = requests.get(gets_url)
    soup = BeautifulSoup(store.content, 'xml')
    stocks_list = []
    for name in soup.find_all('name'):
        stocks_list.append(name.string)
    stocks_id = []
    for id in soup.find_all('id'):
        stocks_id.append(id.text)
    stocks_full = dict(zip(stocks_list, stocks_id))
    return stocks_full


# Получаем список продуктов
def get_products(token):
    url = (protocol + '://' + server + ':' + port + bd + '/api/products?key=' + token.text)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    products_list = []
    for name in soup.find_all('name'):
        products_list.append(name.string)
    products_id = []
    for id in soup.find_all('id'):
        products_id.append(id.text)
    products_full = dict(zip(products_list, products_id))
    return products_full


# Получаем словарь контрагентов (название : id)
def get_suppliers(token):
    url = (protocol + '://' + server + ':' + port + bd + '/api/suppliers?key=' + token.text)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    suppliers_list = []
    for name in soup.find_all('name'):
        suppliers_list.append(name.string)
    suppliers_id = []
    for id in soup.find_all('id'):
        suppliers_id.append(id.text)
    suppliers_full = dict(zip(suppliers_list, suppliers_id))
    return suppliers_full


# Формирование накладной
def data(sup, prod, stocks, date, prices, amounts):
    document = ET.Element('document')
    dateIncoming = ET.SubElement(document, 'dateIncoming')
    useDefaultDocumentTime = ET.SubElement(document, 'useDefaultDocumentTime')
    revenueAccountCode = ET.SubElement(document, 'revenueAccountCode')
    counteragentId = ET.SubElement(document, 'counteragentId')
    items = ET.SubElement(document, 'items')
    item = ET.SubElement(items, 'item')
    productId = ET.SubElement(item, 'productId')
    storeId = ET.SubElement(item, 'storeId')
    price = ET.SubElement(item, 'price')
    amount = ET.SubElement(item, 'amount')
    discountSum = ET.SubElement(item, 'discountSum')
    sum = ET.SubElement(item, 'sum')
    dateIncoming.text = date
    useDefaultDocumentTime.text = 'true'
    revenueAccountCode.text = '4.01'
    counteragentId.text = str(sup['api_test'])  # Считать название покупателя со страницы
    productId.text = str(prod['Кофе зерновой'])  # Считать название продукта со страницы
    storeId.text = str(stocks['test_goose'])  # Считать название склада отгрузки со страницы
    price.text = prices  # цена за 1 шт
    amount.text = amounts  # количество
    discountSum.text = '0'  # скидка
    sum.text = str(float(amounts) * float(prices))  # сумма (цена * количество)
    new_doc = ET.tostring(document)
    # xml_doc = open("RN.xml", "w")
    # xml_doc.write(str(new_doc))
    return new_doc


# Загрузка накладной
def post(token, doc):
    post_url = (
            protocol + '://' + server + ':' + port + bd + '/api/documents/import/outgoingInvoice?&key=' + token.text)
    headers = {'Content-Type': 'application/xml'}  # set what your server accepts
    answer = str(requests.post(post_url, data=doc, headers=headers))
    return answer


def bs4_scrapper():
    pass


# Получение ценовых категорий
def category_price(token):
    url = (
            protocol + '://' + server + ':' + port + bd + '/api/v2/entities/priceCategories/?includeDeleted=true?&key='
            + token.text
    )
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    c = soup.find('p').__dict__
    cc = c['contents']
    ccc = cc[0]
    aa = ccc.string
    category_id_1 = aa[51:87:]
    category_id_2 = aa[223:259:]
    category_id = [category_id_1, category_id_2]
    category_name_1 = aa[97:109:]
    category_name_2 = aa[269:279:]
    category_name = [category_name_1, category_name_2]
    categories_full = dict(zip(category_name, category_id))
    return categories_full

