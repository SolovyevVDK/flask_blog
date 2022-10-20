# Импорт библиотек.
from flask import Flask, render_template, request, redirect
from werkzeug import Response
from functions import auth, get_stocks, get_products, get_suppliers, date_now, logout
import requests
from variables import protocol, port, server, bd

# Сначала нужно считать данные из БД(скорее всего встроенной в питон SQL)
# Сделать отдельную кнопку "Выгрузить данные из айко", в нее зашить запрос из айко, после хранить их БД
# Данные - номенклатура, склады и список контрагентов из айко
# Автоматический склад - "Заявка", выбор все равно должен быть
# Рядом с позициями вводится количество
# Галочка о проводке
# Количество строк зависит от вводимых данных(заполнил строку, добавилась еще)

# Определите приложение.
app = Flask(__name__)


# Определите базовый маршрут URI и функцию.
@app.route('/')
def auth_page() -> 'html':
    return render_template('auth_page_1.html',
                           the_title='Авторизация')


@app.route('/auth', methods=['POST'])
def main_page() -> str:
    global login
    login = request.form['login']
    global password
    password = request.form['password']
    if str(auth(login=str(login), password=str(password))) == '<Response [200]>':
        return redirect("/main_page", code=301)
    else:
        return render_template('error_page.html',
                               the_title='Нужно еще пробовать')


@app.route("/main_page", methods=['post', 'get'])
def test_redirect() -> str:
    token = auth(login=login, password=password)
    print(token)
    stocks = get_stocks(token)
    stocks_name = list(stocks.keys())
    products = get_products(token)
    products_name = list(products.keys())
    suppliers = get_suppliers(token)
    suppliers_name = list(suppliers.keys())
    logout(token)
    return render_template("main_page_2.html",
                           the_title='Бланк заявки',
                           stocks_list=stocks_name,
                           other_inf='Переменная для будущего',
                           prod_list=products_name,
                           suppliers_list=suppliers_name,
                           datetime_now=date_now)


# Запуск
if __name__ == "__main__":
    app.run(debug=True)
