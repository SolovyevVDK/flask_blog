import datetime
import re
import requests
import hashlib
from bs4 import BeautifulSoup
import xml
import os
import csv
import xml.etree.ElementTree as ET

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
def data(sup, prod, stock, date, prices, amounts, prodlen):
    document = ET.Element('document')
    dateIncoming = ET.SubElement(document, 'dateIncoming')
    useDefaultDocumentTime = ET.SubElement(document, 'useDefaultDocumentTime')
    revenueAccountCode = ET.SubElement(document, 'revenueAccountCode')
    counteragentId = ET.SubElement(document, 'counteragentId')
    items = ET.SubElement(document, 'items')
    for i in range(prodlen):
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
        counteragentId.text = sup  # Считать название покупателя со страницы
        productId.text = prod[i]  # Считать название продукта со страницы
        storeId.text = stock  # Считать название склада отгрузки со страницы
        price.text = prices[prod[i]]  # цена за 1 шт
        amount.text = amounts[prod[i]]  # количество
        discountSum.text = '0'  # скидка
        sum.text = str(float(prices[prod[i]]) * float(amounts[prod[i]]))  # сумма (цена * количество)
    new_doc = ET.tostring(document)
    # xml_doc = open("RN.xml", "w")
    # xml_doc.write(str(new_doc))
    return new_doc


# Загрузка накладной
def post(token, doc):
    post_url = (
            protocol + '://' + server + ':' + port + bd + '/api/documents/import/outgoingInvoice?&key=' + token.text)
    headers = {'Content-Type': 'application/xml'}
    answer = str(requests.post(post_url, data=doc, headers=headers))
    return answer


def bs4_scrapper():
    url = 'http://127.0.0.1:5000/main_page'
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'xml')
    date_time = soup.find(class_='prod')
    return date_time


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


# Получение прайс-листа поставщика /api/suppliers/37/pricelist?key=
# Выводит { название номенклатуры у нас : название номенклатуры у поставщика }
def pricelist_supplier_name(token, supplier):
    url = (protocol + '://' + server + ':' + port + bd + '/api/suppliers?key=' + token.text)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    suppliers_list = []
    for name in soup.find_all('name'):
        suppliers_list.append(name.string)
    suppliers_code = []
    for code in soup.find_all('code'):
        suppliers_code.append(code.text)
    suppliers_full = dict(zip(suppliers_list, suppliers_code))
    code = suppliers_full[supplier]
    price_url = (protocol + '://' + server + ':' + port + bd + '/api/suppliers/' + code +
                 '/pricelist?key=' + token.text + '&code=' + code)
    res = requests.get(price_url)
    soup_2 = BeautifulSoup(res.content, 'xml')
    our_product_name = []
    for name in soup_2.find_all('nativeProductName'):
        our_product_name.append(name.string)
    them_product = []
    for name in soup_2.find_all('supplierProductName'):
        them_product.append(name.string)
    pricelist = dict(zip(our_product_name, them_product))
    return pricelist


def pricelist_supplier_id(token, supplier):
    url = (protocol + '://' + server + ':' + port + bd + '/api/suppliers?key=' + token.text)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    suppliers_list = []
    for name in soup.find_all('name'):
        suppliers_list.append(name.string)
    suppliers_code = []
    for code in soup.find_all('code'):
        suppliers_code.append(code.text)
    suppliers_full = dict(zip(suppliers_list, suppliers_code))
    code = suppliers_full[supplier]
    price_url = (protocol + '://' + server + ':' + port + bd + '/api/suppliers/' + code +
                 '/pricelist?key=' + token.text + '&code=' + code)
    res = requests.get(price_url)
    soup_2 = BeautifulSoup(res.content, 'xml')
    our_product_name = []
    for name in soup_2.find_all('nativeProductName'):
        our_product_name.append(name.string)
    them_product = []
    for name in soup_2.find_all('supplierProduct'):
        them_product.append(name.string)
    pricelist = dict(zip(our_product_name, them_product))
    return pricelist


def pricelist_supplier_price(token, supplier):
    url = (protocol + '://' + server + ':' + port + bd + '/api/suppliers?key=' + token.text)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    suppliers_list = []
    for name in soup.find_all('name'):
        suppliers_list.append(name.string)
    suppliers_code = []
    for code in soup.find_all('code'):
        suppliers_code.append(code.text)
    suppliers_full = dict(zip(suppliers_list, suppliers_code))
    code = suppliers_full[supplier]
    price_url = (protocol + '://' + server + ':' + port + bd + '/api/suppliers/' + code +
                 '/pricelist?key=' + token.text + '&code=' + code)
    res = requests.get(price_url)
    soup_2 = BeautifulSoup(res.content, 'xml')
    our_product_name = []
    for name in soup_2.find_all('nativeProductName'):
        our_product_name.append(name.string)
    them_product = []
    for name in soup_2.find_all('costPrice'):
        them_product.append(name.string[0:-7:])
    pricelist = dict(zip(our_product_name, them_product))
    return pricelist
