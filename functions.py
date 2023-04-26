import json
import os
import requests
import hashlib
from bs4 import BeautifulSoup
from pathlib import Path
import xml.etree.ElementTree as ET
from variables import protocol, server, port, bd, days_per_order
from datetime import datetime, timedelta

datetime_string = str(datetime.isoformat(datetime.now()))
date_now = datetime_string[0:-7:]
dateto = datetime_string[0: -16]
datefrom = (str((datetime.now() - timedelta(days=days_per_order))))[0:-16]
timedata = date_now[11::].replace(':', '-')
path_to_consignment = Path(Path.cwd(), 'resource_app', 'consignment')
path_to_pricelist = Path(Path.cwd(), 'resource_app', 'pricelist')
path_to_txt = Path(Path.cwd(), 'resource_app', 'txt')
path_to_samples = Path(Path.cwd(), 'resource_app', 'samples')
encod = 'cp1251'


def read_server_data():
    with open(Path(path_to_txt, 'zerver_data.json'), encoding=encod) as file:
        server_data = json.load(file)
    return server_data


# Получение токена
def auth(login, password, server_data):
    sha1pass = hashlib.sha1(password.encode('utf-8')).hexdigest()
    auth_url = (server_data['protocol'] + '://' +
                server_data['server'] + ':' +
                server_data['port'] +
                server_data['bd'] + '/api/auth?login=' + login + '&pass=' + sha1pass)
    token = requests.get(auth_url)
    return token


# Закрытие токена
def logout(token, server_data):
    out_url = (server_data['protocol'] + '://' +
               server_data['server'] + ':' +
               server_data['port'] +
               server_data['bd'] + '/api/logout?key=' + token.text)
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


# Очистка всех БД, используется для синхронизации
def clean_base():
    category = list(read_category().keys())
    for i in category:
        os.remove(Path(path_to_pricelist, f'{i}.txt'))

    os.remove(Path(path_to_pricelist, 'Базовый прайс.txt'))
    os.remove(Path(path_to_txt, 'category.txt'))
    os.remove(Path(path_to_txt, 'orders.txt'))
    os.remove(Path(path_to_txt, 'orders_name_items.txt'))
    os.remove(Path(path_to_txt, 'products_id.txt'))
    os.remove(Path(path_to_txt, 'products_name.txt'))
    os.remove(Path(path_to_txt, 'stocks.txt'))
    os.remove(Path(path_to_txt, 'suppliers.txt'))
    return


# Записать В ЛОГ склады
def write_stocks(token, server_data):
    gets_url = (server_data['protocol'] + '://' +
                server_data['server'] + ':' +
                server_data['port'] +
                server_data['bd'] + '/api/corporation/stores?key=' + token.text)
    store = requests.get(gets_url)
    soup = BeautifulSoup(store.content, 'xml')
    stores = []
    for corporateItemDto in soup.find_all('corporateItemDto'):
        store = {
            "id": corporateItemDto.find('id').string,
            "parentId": corporateItemDto.find('parentId').string,
            "code": corporateItemDto.find('code').string,
            "name": corporateItemDto.find('name').string,
            "type": corporateItemDto.find('type').string
        }
        stores.append(store)
    with open(Path(path_to_txt, 'stocks.json'), 'w', encoding=encod) as file:
        json.dump(stores, file, indent=4, ensure_ascii=False)
    return stores


# Прочитать ИЗ ЛОГА и записать в переменную склады
def read_stocks():
    with open(Path(path_to_txt, 'stocks.json'), encoding=encod) as file:
        stocks = json.load(file)
    return stocks


def products(token, server_data):
    url = (server_data['protocol'] + '://' +
           server_data['server'] + ':' +
           server_data['port'] +
           server_data['bd'] + '/api/products?key=' + token.text)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    result = []
    for productDto in soup.find_all('productDto'):
        try:
            id = productDto.find('id').string
        except AttributeError:
            id = 'None'

        try:
            parentId = productDto.find('parentId').string
        except AttributeError:
            parentId = 'None'

        try:
            num = productDto.find('num').string
        except AttributeError:
            num = 'None'

        try:
            code = productDto.find('code').string
        except AttributeError:
            code = 'None'

        try:
            name = productDto.find('name').string
        except AttributeError:
            name = 'None'

        try:
            productType = productDto.find('productType').string
        except AttributeError:
            productType = 'None'

        try:
            cookingPlaceType = productDto.find('cookingPlaceType').string
        except AttributeError:
            cookingPlaceType = 'None'

        try:
            mainUnit = productDto.find('mainUnit').string
        except AttributeError:
            mainUnit = 'None'

        try:
            productCategory = productDto.find('productCategory').string
        except AttributeError:
            productCategory = 'None'

        eta = {
            "id": id,
            "parentId": parentId,
            "num": num,
            "code": code,
            "name": name,
            "productType": productType,
            "cookingPlaceType": cookingPlaceType,
            "mainUnit": mainUnit,
            "productCategory": productCategory
        }
        result.append(eta)
    with open(Path(path_to_txt, 'products.json'), 'w', encoding=encod) as file:
        json.dump(result, file, indent=4, ensure_ascii=False)
    return result


# Прочитать ИЗ ЛОГА продукты {name:id}
def read_products():
    with open(Path(path_to_txt, 'products.json'), encoding=encod) as file:
        products_new = json.load(file)
    return products_new


# Запись В ЛОГ словарь контрагентов (название : id)
def write_suppliers(token):
    url = (protocol + '://' + server + ':' + port + bd + '/api/suppliers?key=' + token.text)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    # suppliers_list = []
    # for name in soup.find_all('name'):
    #     suppliers_list.append(name.string)
    # suppliers_id = []
    # for id in soup.find_all('id'):
    #     suppliers_id.append(id.text)
    # suppliers_full = dict(zip(suppliers_list, suppliers_id))
    # with open(Path(path_to_txt, 'suppliers.txt'), 'w', encoding=encod) as file:
    #     json.dump(suppliers_full, file, indent=4, ensure_ascii=False)
    suppliers = []
    for employees in soup.find_all('employee'):
        try:
            id = employees.find('id').string
        except AttributeError:
            id = 'None'
        try:
            code = employees.find('code').string
        except AttributeError:
            code = 'None'
        try:
            name = employees.find('name').string
        except AttributeError:
            name = 'None'
        try:
            login = employees.find('login').string
        except AttributeError:
            login = 'None'
        try:
            phone = employees.find('phone').string
        except AttributeError:
            phone = 'None'
        try:
            cellPhone = employees.find('cellPhone').string
        except AttributeError:
            cellPhone = 'None'
        try:
            firstName = employees.find('firstName').string
        except AttributeError:
            firstName = 'None'
        try:
            middleName = employees.find('middleName').string
        except AttributeError:
            middleName = 'None'
        try:
            lastName = employees.find('lastName').string
        except AttributeError:
            lastName = 'None'
        try:
            birthday = employees.find('birthday').string
        except AttributeError:
            birthday = 'None'
        try:
            email = employees.find('email').string
        except AttributeError:
            email = 'None'
        try:
            address = employees.find('address').string
        except AttributeError:
            address = 'None'
        try:
            cardNumber = employees.find('cardNumber').string
        except AttributeError:
            cardNumber = 'None'
        try:
            taxpayerIdNumber = employees.find('taxpayerIdNumber').string
        except AttributeError:
            taxpayerIdNumber = 'None'
        try:
            snils = employees.find('snils').string
        except AttributeError:
            snils = 'None'
        try:
            preferredDepartmentCode = employees.find('preferredDepartmentCode').string
        except AttributeError:
            preferredDepartmentCode = 'None'
        try:
            departmentCodes = employees.find('departmentCodes').string
        except AttributeError:
            departmentCodes = 'None'
        try:
            responsibilityDepartmentCodes = employees.find('responsibilityDepartmentCodes').string
        except AttributeError:
            responsibilityDepartmentCodes = 'None'
        try:
            deleted = employees.find('deleted').string
        except AttributeError:
            deleted = 'None'
        try:
            supplier = employees.find('supplier').string
        except AttributeError:
            supplier = 'None'
        try:
            client = employees.find('client').string
        except AttributeError:
            client = 'None'
        try:
            representsStore = employees.find('representsStore').string
        except AttributeError:
            representsStore = 'None'
        employeer = {
            "id": id,
            "code": code,
            "name": name,
            "login": login,
            "phone": phone,
            "cellPhone": cellPhone,
            "firstName": firstName,
            "middleName": middleName,
            "lastName": lastName,
            "birthday": birthday,
            "email": email,
            "address": address,
            "cardNumber": cardNumber,
            "taxpayerIdNumber": taxpayerIdNumber,
            "snils": snils,
            "preferredDepartmentCode": preferredDepartmentCode,
            "departmentCodes": departmentCodes,
            "responsibilityDepartmentCodes": responsibilityDepartmentCodes,
            "deleted": deleted,
            "supplier": supplier,
            "client": client,
            "representsStore": representsStore
        }
        suppliers.append(employeer)
    with open(Path(path_to_txt, 'suppliers.json'), 'w', encoding=encod) as file:
        json.dump(suppliers, file, indent=4, ensure_ascii=False)
    return suppliers


# Прочитать ИЗ ЛОГА словарь поставщиков
def read_suppliers():
    with open(Path(path_to_txt, 'suppliers.txt'), encoding=encod) as file:
        suppliers = json.load(file)
    return suppliers


# Записать В ЛОГ приказы(весь запрос)
def write_orders(token):
    url = (protocol + '://' + server + ':' + port + bd + '/api/v2/documents/menuChange?dateFrom='
           + datefrom + '&dateTo=' + dateto + '&key=' + token.text)
    res = requests.get(url)
    orders = res.json()['response']
    with open(Path(path_to_txt, 'orders.txt'), 'w', encoding=encod) as file:
        json.dump(orders, file, indent=4, ensure_ascii=False)
    names = []
    items = []
    for i in range(len(orders)):
        names.append(orders[i]['shortName'])
        items.append(orders[i]['items'])

    orders_full = dict(zip(names, items))

    with open(Path(path_to_txt, 'orders_name_items.txt'), 'w', encoding=encod) as file:
        json.dump(orders_full, file, indent=4, ensure_ascii=False)
    return orders_full


# Чтение приказов
def read_orders():
    with open(Path(path_to_txt, 'orders.txt'), encoding=encod) as file:
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
        with open(Path(path_to_txt, 'category.txt'), 'w', encoding=encod) as file:
            json.dump(category_list, file, indent=4, ensure_ascii=False)
    return category_list


# Чтение ИЗ ЛОГА ценовых категорий
def read_category():
    with open(Path(path_to_txt, 'category.txt'), encoding=encod) as file:
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
                try:
                    name = products_id[orders[i]['items'][j]['productId']]
                except KeyError as ex:
                    continue
                base_price = orders[i]['items'][j]['price']
                price_for_category = orders[i]['items'][j]['pricesForCategories']
                di.update({name: base_price})
                for m in range(len(price_for_category)):
                    if price_for_category[m]['categoryId'] == category[n]:
                        d.update({name: price_for_category[m]['price']})
        with open(Path(path_to_pricelist, f'{n}.txt'), 'w', encoding=encod) as fille:
            json.dump(d, fille, indent=4, ensure_ascii=False)

    with open(Path(path_to_pricelist, 'Базовый прайс.txt'), 'w', encoding=encod) as file:
        json.dump(di, file, indent=4, ensure_ascii=False)
    return


def read_category_price(category_name):
    with open(Path(path_to_pricelist, f'{category_name}.txt', encoding=encod)) as file:
        pricelist = json.load(file)
    return pricelist


# Формирование накладной
def data(date, sup, stock, pricelist, amountlist, comments):
    products_name = read_products_name()
    stock_name = read_stocks()
    supplier_name = read_suppliers()
    document = ET.Element('document')
    dateIncoming = ET.SubElement(document, 'dateIncoming')
    useDefaultDocumentTime = ET.SubElement(document, 'useDefaultDocumentTime')
    revenueAccountCode = ET.SubElement(document, 'revenueAccountCode')
    counteragentId = ET.SubElement(document, 'counteragentId')
    defaultStoreId = ET.SubElement(document, 'defaultStoreId')
    defaultStoreId.text = stock_name[stock]
    comment = ET.SubElement(document, 'comment')
    comment.text = 'Сайт. ' + comments
    items = ET.SubElement(document, 'items')
    for key, value in pricelist.items():
        item = ET.SubElement(items, 'item')
        productId = ET.SubElement(item, 'productId')
        price = ET.SubElement(item, 'price')
        amount = ET.SubElement(item, 'amount')
        discountSum = ET.SubElement(item, 'discountSum')
        sum = ET.SubElement(item, 'sum')
        dateIncoming.text = date
        useDefaultDocumentTime.text = 'true'
        revenueAccountCode.text = '4.01'
        counteragentId.text = supplier_name[sup]  # Считать название покупателя со страницы
        productId.text = products_name[key]  # Считать название продукта со страницы
        price.text = str(value)  # цена за 1 шт
        amount.text = str(amountlist[key])  # количество
        discountSum.text = '0'  # скидка
        sum.text = str(float(value) * float(amountlist[key]))  # сумма (цена * количество)
    new_doc = ET.tostring(document)

    elements = []
    allsumm = 0
    for k, v in pricelist.items():
        el = {
            "product": k,
            "price": float(v),
            "amount": float(amountlist[k]),
            "summ": round((float(float(v) * float(amountlist[k]))), 2)
        }
        elements.append(el)
        allsumm += float(float(v) * float(amountlist[k]))

    manifesto = {
        "stock": stock,
        "supplier": sup,
        "comment": comments,
        "date": (str(date)).replace('T', ' '),
        "summ": round(allsumm, 2),
        "items": elements
    }
    dvk = ((str(date)).split("T"))[0].replace("-", "_")
    tvk = ((str(date)).split("T"))[1].replace(":", "_")
    with open(Path(path_to_consignment,
                   f'consignment_{dvk}_{tvk}.json'),
              'w', encoding=encod) as file:
        json.dump(manifesto, file, indent=4, ensure_ascii=False)
    return new_doc


# Загрузка накладной
def post(token, doc):
    post_url = (
            protocol + '://' + server + ':' + port + bd + '/api/documents/import/outgoingInvoice?&key=' + token.text)
    headers = {'Content-Type': 'application/xml'}
    answer = str(requests.post(post_url, data=doc, headers=headers))
    return answer


def invoice_by_number(token, num):
    out_url = (
            protocol + '://' + server + ':' + port + bd + '/api/documents/export/outgoingInvoice/byNumber?key='
            + token.text + '&number=' + num + '&currentYear=true'
    )
    invoice = requests.get(out_url).text
    return invoice


def all_invoices(token, supid):
    url = (
            protocol + '://' + server + ':' + port + bd + '/api/documents/export/outgoingInvoice?key='
            + token.text + '&from=2023-01-01&to=2023-16-02' + '&supplierId=' + supid
    )
    invoices = requests.get(url).text
    return invoices
