import json
import os

import requests
import hashlib
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

from variables import protocol, server, port, bd, days_per_order
from datetime import datetime, timedelta

datetime_string = str(datetime.now())
date_now = datetime_string[0:-7:]
dateto = datetime_string[0: -16]
datefrom = (str((datetime.now() - timedelta(days=days_per_order))))[0:-16]


def bs4_scrap(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.content, features="lxml")
    cat_name = soup.find('ul', class_='cat_name')
    print(cat_name)
    return


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


# Запись ВСЕГО
def all_write(token):
    write_category(token)
    write_stocks(token)
    write_suppliers(token)
    write_products_id(token)
    write_products_name(token)
    write_orders(token)
    category_pricelist()


# Записать В ЛОГ склады
def write_stocks(token):
    gets_url = (protocol + '://' + server + ':' + port + bd + '/api/corporation/stores?key=' + token.text)
    store = requests.get(gets_url)
    soup = BeautifulSoup(store.content, 'xml')
    with open(f'log/xml/stocks_{dateto}.xml', 'w', encoding='utf-8') as file:
        file.write(str(soup))
    stocks_list = []
    for name in soup.find_all('name'):
        stocks_list.append(name.string)
    stocks_id = []
    for id in soup.find_all('id'):
        stocks_id.append(id.text)
    stocks_full = dict(zip(stocks_list, stocks_id))
    with open('log/txt/stocks.txt', 'w', encoding='utf-8') as file:
        json.dump(stocks_full, file, indent=4, ensure_ascii=False)
    return


# Прочитать ИЗ ЛОГА и записать в переменную склады
def read_stocks():
    with open('log/txt/stocks.txt', encoding='utf-8') as file:
        stocks = json.load(file)
    return stocks


# Записываем список продуктов В ЛОГ {name:id}
def write_products_name(token):
    url = (protocol + '://' + server + ':' + port + bd + '/api/products?key=' + token.text)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    with open(f'log/xml/products_name_{dateto}.xml', 'w', encoding='utf-8') as file:
        file.write(str(soup))
    products_list = []
    for name in soup.find_all('name'):
        products_list.append(name.string)
    products_id = []
    for id in soup.find_all('id'):
        products_id.append(id.text)
    products_full = dict(zip(products_list, products_id))
    with open('log/txt/products_name.txt', 'w', encoding='utf-8') as file:
        json.dump(products_full, file, indent=4, ensure_ascii=False)
    return products_full


# Прочитать ИЗ ЛОГА продукты {name:id}
def read_products_name():
    with open('log/txt/products_name.txt', encoding='utf-8') as file:
        products_name = json.load(file)
    return products_name


# Записать список продуктов В ЛОГ {id:name}
def write_products_id(token):
    url = (protocol + '://' + server + ':' + port + bd + '/api/products?key=' + token.text)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    with open(f'log/xml/products_id_{dateto}.xml', 'w', encoding='utf-8') as file:
        file.write(str(soup))
    products_list = []
    for name in soup.find_all('name'):
        products_list.append(name.string)
    products_id = []
    for id in soup.find_all('id'):
        products_id.append(id.text)
    products_full = dict(zip(products_id, products_list))
    with open('log/txt/products_id.txt', 'w', encoding='utf-8') as file:
        json.dump(products_full, file, indent=4, ensure_ascii=False)
    return products_full


# Прочитать ИЗ ЛОГА {id:name} продукты
def read_products_id():
    with open('log/txt/products_id.txt', encoding='utf-8') as file:
        products_id = json.load(file)
    return products_id


# Запись В ЛОГ словарь контрагентов (название : id)
def write_suppliers(token):
    url = (protocol + '://' + server + ':' + port + bd + '/api/suppliers?key=' + token.text)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    with open(f'log/xml/suppliers_{dateto}.xml', 'w', encoding='utf-8') as file:
        file.write(str(soup))
    suppliers_list = []
    for name in soup.find_all('name'):
        suppliers_list.append(name.string)
    suppliers_id = []
    for id in soup.find_all('id'):
        suppliers_id.append(id.text)
    suppliers_full = dict(zip(suppliers_list, suppliers_id))
    with open('log/txt/suppliers.txt', 'w', encoding='utf-8') as file:
        json.dump(suppliers_full, file, indent=4, ensure_ascii=False)
    return suppliers_full


# Прочитать ИЗ ЛОГА словарь поставщиков
def read_suppliers():
    with open('log/txt/suppliers.txt', encoding='utf-8') as file:
        suppliers = json.load(file)
    return suppliers


# Записать В ЛОГ приказы(весь запрос)
def write_orders(token):
    url = (protocol + '://' + server + ':' + port + bd + '/api/v2/documents/menuChange?dateFrom='
           + datefrom + '&dateTo=' + dateto + '&key=' + token.text)
    res = requests.get(url)
    orders = res.json()['response']
    with open('log/txt/orders.txt', 'w', encoding='utf-8') as file:
        json.dump(orders, file, indent=4, ensure_ascii=False)
    names = []
    items = []
    for i in range(len(orders)):
        names.append(orders[i]['shortName'])
        items.append(orders[i]['items'])

    orders_full = dict(zip(names, items))

    with open('log/txt/orders_name_items.txt', 'w', encoding='utf-8') as file:
        json.dump(orders_full, file, indent=4, ensure_ascii=False)
    return orders_full


# Чтение приказов
def read_orders():
    with open('log/txt/orders.txt', encoding='utf-8') as file:
        orders = json.load(file)
    return orders


# Запись В ЛОГ ценовых категорий
def write_category(token):
    url = (protocol + '://' + server + ':' + port + bd + '/api/v2/entities/priceCategories/?includeDeleted=true?&key='
           + token.text)
    response = requests.get(url)
    category = response.json()['response']
    names = []
    ids = []
    for i in range(len(category)):
        name = category[i]['name']
        id = category[i]['id']
        names.append(name)
        ids.append(id)
        category_list = dict(zip(names, ids))
        with open('log/txt/category.txt', 'w', encoding='utf-8') as file:
            json.dump(category_list, file, indent=4, ensure_ascii=False)
    return category_list


# Чтение ИЗ ЛОГА ценовых категорий
def read_category():
    with open('log/txt/category.txt', encoding='utf-8') as file:
        category = json.load(file)
    return category


def category_pricelist():
    products_id = read_products_id()
    category = read_category()
    orders = read_orders()
    category_name = list(category.keys())

    di = {}
    for n in category_name:
        d = {}
        for i in range(len(orders)):
            for j in range(len(orders[i]['items'])):
                name = products_id[orders[i]['items'][j]['productId']]
                base_price = orders[i]['items'][j]['price']
                price_for_category = orders[i]['items'][j]['pricesForCategories']
                di.update({name: base_price})
                for m in range(len(price_for_category)):
                    if price_for_category[m]['categoryId'] == category[n]:
                        d.update({name: price_for_category[m]['price']})
        with open(f'log/pricelist/{n}.json', 'w', encoding='utf-8') as fille:
            json.dump(d, fille, indent=4, ensure_ascii=False)

    with open('log/pricelist/Базовый прайслист.json', 'w', encoding='utf-8') as file:
        json.dump(di, file, indent=4, ensure_ascii=False)
    return


def read_category_price(category_name):
    with open(f'log/pricelist/{category_name}.json', encoding='utf-8') as file:
        pricelist = json.load(file)
    return pricelist


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
    with open(f'log/consignment/{date_now}_consignment.txt', 'w', encoding='utf-8') as file:
        file.write()
    return new_doc


# Загрузка накладной
def post(token, doc):
    post_url = (
            protocol + '://' + server + ':' + port + bd + '/api/documents/import/outgoingInvoice?&key=' + token.text)
    headers = {'Content-Type': 'application/xml'}
    answer = str(requests.post(post_url, data=doc, headers=headers))
    return answer


