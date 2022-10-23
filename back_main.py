from functions import get_stocks, get_products, get_suppliers, logout, auth, data, post, category_price
from datetime import datetime


datetime_string = str(datetime.now())
date_now = datetime_string[0:-7:]

token = auth(login='admin', password='restoRtest')  # login and pass со страницы от пользователя
# stocks = get_stocks(token)
# stocks_name = list(stocks.keys())
# prod = get_products(token)
# prod_name = list(prod.keys())
# suppliers = get_suppliers(token)
category = category_price(token)
# suppliers_name = list(suppliers.keys())
# data = data(sup=suppliers, prod=prod, stocks=stocks,
#             date=date_now, prices='100', amounts='5')  # все переменные собираются со страницы
# go_rn = post(token=token, doc=data)

logout(token)

# print(data)
# print(go_rn)
# print(stocks)
# print(len(prod_name))
# print(go_rn)
# print(stocks['test_goose'])
# print(suppliers)
print(category)
print(token.text)



