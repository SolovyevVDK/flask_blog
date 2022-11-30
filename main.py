# Импорт библиотек.
import json
from datetime import datetime

from flask import Flask, render_template, request, redirect
from werkzeug import Response
from functions import auth, date_now, logout, read_suppliers, read_category, read_stocks, read_products_name, \
    read_category_price, data, post, all_write
import requests

from variables import protocol, server, port, bd


# Определите приложение.
app = Flask(__name__)


# Определите базовый маршрут URI и функцию.
@app.route('/auth', methods=['post', 'get'])
def auth_page() -> 'html':
    return render_template('auth.html',
                           the_title='Авторизация')


@app.route("/", methods=['post', 'get'])
def main_page() -> 'html':
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
                           datetime_now=date_now)


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
    return render_template("main_finally.html",
                           the_title='Бланк заявки',
                           datetime_now=date_now,
                           stock=chosen_stock,
                           supplier=chosen_supplier,
                           category=chosen_category,
                           pricelist=pricelist,
                           amount_list=amount_list,
                           order=order,
                           am=name_amount)


@app.route("/send", methods=['post'])
def send() -> str:
    products = list(pricelist.keys())
    prices = list(pricelist.values())
    doc = data(sup=chosen_supplier, stock=chosen_stock, date=date_now, prod=products, prices=prices,
               amounts=amount_list, prodlen=len(products))
    login = request.form['login']
    password = request.form['password']
    token = auth(login, password)
    post(token=token, doc=doc)
    with open('log/consignment/past_consignment.xml', 'w', encoding="utf-8") as file:
        file.write(str(doc))
    logout(token)
    return render_template("nice.html",
                           the_title='Накладная отправлена')


@app.route("/synch", methods=['post', 'get'])
def synch() -> 'html':
    login = request.form['login']
    password = request.form['password']
    token = auth(login, password)
    all_write(token)
    logout(token)
    return render_template("nice.html",
                           the_title='Синхронизация выполнена')


# Запуск
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug="True")
