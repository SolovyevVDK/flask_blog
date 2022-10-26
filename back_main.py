from pprint import pprint

from functions import get_stocks, get_products, get_suppliers, logout, auth, data, post, category_price
from datetime import datetime


datetime_string = str(datetime.now())
date_now = datetime_string[0:-7:]


# login = input("Введите логин: ")
# password = input("Введите пароль: ")
login = 'admin'
password = 'restoRtest'
token = auth(login=login, password=password)  # login and pass со страницы от пользователя
stocks = get_stocks(token)
stocks_name = list(stocks.keys())
print(f"Доступные склады: {stocks_name}")
prod = get_products(token)
prod_name = list(prod.keys())
print(f"Доступные продукты: {prod_name}")
suppliers = get_suppliers(token)
suppliers_name = list(suppliers.keys())
print(f"Доступные поставщики: {suppliers_name}")
# category = category_price(token)
lenprod = int(input("Введите количество позиций: "))
test_stock = input("Введите склад: ")
test_sup = input("Введите поставщика: ")
products = []
my_prices = []
my_amounts = []
for i in range(lenprod):
    test_prod = input(f"Введите {i+1} продукт: ")
    my_price = input(f'Введите стоимость {i+1} продукта: ')
    my_amount = input(f'Введите количество {i+1} продукта: ')
    my_amounts.append(my_amount)
    my_prices.append(my_price)
    products.append(prod[f'{test_prod}'])

prices = dict(zip(products, my_prices))    # Ключ - id продукта, значение - стоимость продукта
amounts = dict(zip(products, my_amounts))     # Ключ - id продукта, значение - количество продукта


data = data(sup=suppliers[f'{test_sup}'], prod=products, stock=stocks[f'{test_stock}'],
            date=date_now, prices=prices, amounts=amounts, prodlen=lenprod)  # все переменные собираются со страницы
print(data)
go_rn = post(token=token, doc=data)

logout(token)

# Сделать кнопку Сформировать расходную накладную и отдельно Отправить накладную
# это для выгрузки суммы всей накладной

# print(data)
# print(go_rn)
# print(stocks)
# print(len(prod_name))
# print(go_rn)
# print(stocks['test_goose'])
# print(suppliers)



