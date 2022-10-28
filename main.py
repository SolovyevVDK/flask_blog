# Импорт библиотек.
from flask import Flask, render_template, request, redirect
from werkzeug import Response
from functions import auth, get_stocks, get_products, get_suppliers, date_now, logout, category_price
import requests

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
@app.route('/')
def auth_page() -> 'html':
    return render_template('auth_page_1.html',
                           the_title='Авторизация')


@app.route('/auth', methods=['POST'])
def main_page() -> str:
    login = request.form['login']
    password = request.form['password']
    global token
    token = auth(login=str(login), password=str(password))
    # print(token.text)
    if str(auth(login=login, password=password)) == '<Response [200]>':
        return redirect("/main_page", code=301)
    else:
        return render_template('error_page.html',
                               the_title='Неверный логин или пароль, вернитесь на страницу авторизации')


@app.route("/main_page", methods=['post', 'get'])
def main_page_zajavka() -> 'html':
    stocks = get_stocks(token)
    stocks_name = list(stocks.keys())
    products = get_products(token)
    products_name = list(products.keys())
    suppliers = get_suppliers(token)
    suppliers_name = list(suppliers.keys())
    category = category_price(token)
    category_name = list(category.keys())
    print(token.text)
    # logout(token)
    # consign_date = request.form['datetime']
    # consign_stock = request.form['stock']
    # consign_supplier = request.form['suppliers']
    return render_template("main_page_2.html",
                           the_title='Бланк заявки',
                           stocks_list=stocks_name,
                           other_inf='Переменная для будущего',
                           prod_list=products_name,
                           suppliers_list=suppliers_name,
                           category_list=category_name,
                           datetime_now=date_now)


@app.route("/logout", methods=['post'])
def send():
    logout(token)
    return redirect("/", code=301)


# Запуск
if __name__ == "__main__":
    app.run(debug=True)
