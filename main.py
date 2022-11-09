# Импорт библиотек.
import json

from flask import Flask, render_template, request, redirect
from werkzeug import Response
from functions import auth, date_now, logout, read_suppliers, read_category, read_stocks, read_products_name
import requests

from variables import protocol, server, port, bd

# Сначала нужно считать данные из БД(скорее всего встроенной в питон SQLite)?
# Сделать отдельную кнопку "Выгрузить данные из айко", в нее зашить запрос из айко, после хранить их БД?
# Данные - номенклатура, ценовые категории, склады и список контрагентов из айко
# Автоматический склад - "Заявка", выбор все равно должен быть?
# Рядом с позициями вводится количество
# Галочка о проводке?
# Количество строк зависит от вводимых данных(заполнил строку, добавилась еще)

# Определите приложение.
app = Flask(__name__)


# Определите базовый маршрут URI и функцию.
@app.route('/auth', methods=['post', 'get'])
def auth_page() -> 'html':
    return render_template('auth_page_1.html',
                           the_title='Авторизация')


@app.route('/settings', methods=['post', 'get'])
def settings() -> 'html':
    suppliers = list(read_suppliers().keys())
    categories = list(read_category().keys())
    # global cat_name
    # cat_name = request.form['cat_name']
    return render_template('settings.html',
                           the_title='Настройки',
                           suppliers=suppliers,
                           categories=categories)


@app.route('/settings_1', methods=['post'])
def set_complete() -> 'html':
    suppliers = list(read_suppliers().keys())
    cat_name = request.form['cat_name']
    print(cat_name)
    d = dict(zip(suppliers, cat_name))
    with open('supcat.json', 'w', encoding='utf-8') as file:
        json.dump(d, file, indent=4, ensure_ascii=False)
    return render_template('settings.html',
                           the_title='Настройки',
                           suppliers=suppliers,
                           cat_name=suppliers)


@app.route("/", methods=['post', 'get'])
def main_page() -> 'html':
    stocks_name = list(read_stocks().keys())
    products_name = list(read_products_name().keys())
    suppliers_name = list(read_suppliers().keys())
    return render_template("main.html",
                           the_title='Бланк заявки',
                           stocks_list=stocks_name,
                           prod_list=products_name,
                           suppliers_list=suppliers_name,
                           datetime_now=date_now)


# Запуск
if __name__ == "__main__":
    app.run(host='0.0.0.0')
