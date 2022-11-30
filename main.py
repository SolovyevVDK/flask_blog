import os.path
from datetime import datetime

from flask import Flask, render_template, request
from functions import auth, date_now, logout, read_suppliers, read_category, read_stocks, read_products_name, \
    read_category_price, data, post, all_write, clean_base

from variables import protocol, server, port, bd, days_per_order

# Определите приложение.
app = Flask(__name__)


# Определите базовый маршрут URI и функцию.
@app.route('/auth', methods=['post', 'get'])
def auth_page() -> 'html':
    return render_template('auth.html',
                           the_title='Авторизация')


@app.route("/", methods=['post', 'get'])
def main_page() -> 'html':
    with open('log/txt/synch.txt', 'r', encoding='utf-8') as file:
        synch_time = file.read()
    stocks_name = list(read_stocks().keys())
    products_name = list(read_products_name().keys())
    suppliers_name = list(read_suppliers().keys())
    category_name = list(read_category().keys())
    category_name.append('Базовый прайс')
    return render_template("main.html",
                           the_title='Бланк заявки',
                           stocks_list=stocks_name,
                           prod_list=products_name,
                           suppliers_list=suppliers_name,
                           category_list=category_name,
                           datetime_now=date_now,
                           synch_time=synch_time)


@app.route("/main_complete", methods=['post', 'get'])
def main_page_1() -> 'html':
    global chosen_stock, chosen_supplier, chosen_category, pricelist
    chosen_stock = request.form['stock']
    chosen_supplier = request.form['supplier']
    chosen_category = request.form['categories']
    pricelist = read_category_price(chosen_category)
    order = list(pricelist.keys())
    order.sort()
    return render_template("main_complete.html",
                           the_title='Бланк заявки',
                           datetime_now=date_now,
                           stock=chosen_stock,
                           supplier=chosen_supplier,
                           category=chosen_category,
                           pricelist=pricelist,
                           order=order)


@app.route("/main_finally", methods=['post', 'get'])
def main_page_2() -> 'html':
    global amount_list, name_amount
    amount_list = request.form.getlist('amount')
    order = list(pricelist.keys())
    order.sort()
    name_amount = dict(zip(order, amount_list))
    amount_name = dict(zip(amount_list, order))
    new_name_amount = {}
    for key, value in name_amount.items():
        if value == '0':
            continue
        else:
            new_name_amount[key] = value

    global last_products, last_amounts, last_prices
    last_products = list(new_name_amount.keys())
    last_amounts = list(new_name_amount.values())
    new_pricelist = {}
    for key, value in pricelist.items():
        if key not in last_products:
            continue
        else:
            new_pricelist[key] = value
    last_prices = list(new_pricelist.values())
    print(last_amounts)
    print(last_prices)
    summ = []
    for i in range(0, len(last_prices)):
        summ.append(float(last_amounts[i]) * float(new_pricelist[amount_name[last_amounts[i]]]))

    print(summ)
    last_summ = sum(summ)
    return render_template("main_finally.html",
                           the_title='Бланк заявки',
                           datetime_now=date_now,
                           stock=chosen_stock,
                           supplier=chosen_supplier,
                           category=chosen_category,
                           pricelist=pricelist,
                           amount_list=amount_list,
                           order=order,
                           am=name_amount,
                           sum=last_summ)


@app.route("/send", methods=['post'])
def send() -> str:
    doc = data(sup=chosen_supplier, stock=chosen_stock, date=date_now, prod=last_products, prices=last_prices,
               amounts=last_amounts, prodlen=len(last_products))
    login = request.form['login']
    password = request.form['password']
    token = auth(login, password)
    post(token=token, doc=doc)
    logout(token)
    return render_template("nice.html",
                           the_title='Накладная отправлена')


@app.route("/synch", methods=['post', 'get'])
def synch() -> 'html':
    synch_time = (str(datetime.now()))[0:-7]
    with open('log/txt/synch.txt', 'w', encoding='utf-8') as file:
        file.write(str(synch_time))
    login = request.form['login']
    password = request.form['password']
    token = auth(login, password)
    all_write(token)
    logout(token)
    return render_template("nice.html",
                           the_title='Синхронизация выполнена')


@app.route("/admin", methods=['post', 'get'])
def admin_page() -> 'html':
    return render_template("admin.html",
                           the_title="Настройки синхронизации с iiko",
                           protocol=protocol,
                           server=server,
                           port=port,
                           bd=bd,
                           days_per_order=days_per_order)


@app.route("/admin_nice", methods=['post', 'get'])
def admin_page_2() -> 'html':
    if os.path.exists('log/txt/category.txt'):
        clean_base()

    new_protocol = request.form['protocol']
    new_server = request.form['server']
    new_port = request.form['port']
    new_bd = request.form['bd']
    new_days_per_order = request.form['days_per_order']
    with open('variables.py', 'w', encoding='utf-8') as file:
        file.write(f'protocol = "{str(new_protocol)}"\n')
        file.write(f'server = "{str(new_server)}"\n')
        file.write(f'port = "{str(new_port)}"\n')
        file.write(f'bd = "{str(new_bd)}"\n')
        file.write(f'days_per_order = {int(new_days_per_order)}\n')
    return render_template("admin.html",
                           the_title="Настройки сохранены",
                           protocol=new_protocol,
                           server=new_server,
                           port=new_port,
                           bd=new_bd,
                           days_per_order=new_days_per_order)


# Запуск
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug="True")
