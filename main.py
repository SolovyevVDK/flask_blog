import json
import os.path
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request
from functions import auth, date_now, logout, read_suppliers, read_category, read_stocks, read_products_name, \
    read_category_price, data, post, all_write, clean_base, path_to_txt, path_to_samples, encod
from variables import protocol, server, port, bd, days_per_order

chosen_stock = None
chosen_supplier = None
chosen_category = None
pricelist = None
amounts = None
amountlist = None
last_products = None
last_amounts = None
last_prices = None
chosen_time = None
chosen_date = None
sample_stock = None
sample_supplier = None
sample_category = None
sample_full = None
pricelist_sample = None
new_amountlist = None
new_pricelist = None
sample_pricelist = None
sample_name = None

# Определите приложение.
app = Flask(__name__)


# Определите базовый маршрут URI и функцию.
@app.route('/auth', methods=['post', 'get'])
def auth_page() -> 'html':
    with open(Path(path_to_txt, 'synch.txt'), 'r', encoding=encod) as file:
        synch_time = file.read()
    try:
        return render_template('auth.html',
                               the_title='Авторизация',
                               synch_time=synch_time)
    except Exception as ex:
        return render_template("error.html",
                               type_ex=ex.__class__,
                               ex=ex)


@app.route("/", methods=['post', 'get'])
def main_page() -> 'html':
    with open(Path(path_to_txt, 'synch.txt'), 'r', encoding=encod) as file:
        synch_time = file.read()
    try:
        cat = os.path.exists(Path(path_to_txt, 'category.txt'))
        ord = os.path.exists(Path(path_to_txt, 'orders.txt'))
        oni = os.path.exists(Path(path_to_txt, 'orders_name_items.txt'))
        pi = os.path.exists(Path(path_to_txt, 'products_id.txt'))
        pn = os.path.exists(Path(path_to_txt, 'products_name.txt'))
        st = os.path.exists(Path(path_to_txt, 'stocks.txt'))
        sup = os.path.exists(Path(path_to_txt, 'suppliers.txt'))
        if not cat or not ord or not oni or not pi or not pn or not st or not sup:
            return render_template('auth.html',
                                   the_title='Нет данных',
                                   title_2='На сервере нет данных из iiko, выполните синхронизацию')
        else:
            stocks_name = list(read_stocks().keys())
            products_name = list(read_products_name().keys())
            suppliers_name = list(read_suppliers().keys())
            category_name = list(read_category().keys())
            category_name.append('Базовый прайс')
            return render_template("invoice_create.html",
                                   the_title='Бланк заявки',
                                   stocks_list=stocks_name,
                                   prod_list=products_name,
                                   suppliers_list=suppliers_name,
                                   category_list=category_name,
                                   synch_time=synch_time)
    except Exception as ex:
        return render_template("error.html",
                               type_ex=ex.__class__,
                               ex=ex)


@app.route("/main_complete", methods=['post', 'get'])
def main_page_1() -> 'html':
    try:
        global chosen_stock, chosen_supplier, chosen_category, pricelist
        chosen_stock = request.form['stock']
        chosen_supplier = request.form['supplier']
        chosen_category = request.form['categories']
        pricelist = read_category_price(chosen_category)
        pricelist = dict(sorted(pricelist.items()))
        order = list(pricelist.keys())
        return render_template("main_complete.html",
                               the_title='Бланк заявки',
                               datetime_now=date_now,
                               stock=chosen_stock,
                               supplier=chosen_supplier,
                               category=chosen_category,
                               pricelist=pricelist,
                               order=order)
    except Exception as ex:
        return render_template("error.html",
                               type_ex=ex.__class__,
                               ex=ex)


@app.route("/main_finally", methods=['post', 'get'])
def main_page_2() -> 'html':
    try:
        global amounts, amountlist, new_amountlist, new_pricelist
        amounts = request.form.getlist('amount')
        amountlist = dict(zip(list(pricelist.keys()), amounts))
        amount_name = dict(zip(amounts, list(pricelist.keys())))
        new_amountlist = {}
        for key, value in amountlist.items():
            if value == '0':
                continue
            else:
                new_amountlist[key] = value
        new_pricelist = {}
        for key, value in pricelist.items():
            if key not in list(new_amountlist.keys()):
                continue
            else:
                new_pricelist[key] = value
        summ = []
        for key, value in new_pricelist.items():
            for key_2, value_2 in new_amountlist.items():
                if key == key_2:
                    summ.append(float(value) * float(value_2))
                else:
                    continue
        last_summ = sum(summ)
        return render_template("main_finally.html",
                               the_title='Бланк заявки',
                               time=chosen_time,
                               date=chosen_date,
                               stock=chosen_stock,
                               supplier=chosen_supplier,
                               category=chosen_category,
                               pricelist=pricelist,
                               amount_list=amounts,
                               order=list(pricelist.keys()),
                               am=amountlist,
                               sum=last_summ)
    except Exception as ex:
        return render_template("error.html",
                               type_ex=ex.__class__,
                               ex=ex)


@app.route("/send", methods=['post'])
def send() -> str:
    try:
        try_date = str(chosen_date + 'T' + chosen_time + ':00')
        comment = request.form['comment-area']
        doc = data(sup=chosen_supplier, stock=chosen_stock, date=try_date, pricelist=new_pricelist,
                   amountlist=new_amountlist, comments=comment)
        login = request.form['login']
        password = request.form['password']
        token = auth(login, password)
        str_token = str(token)
        if str_token == '<Response [200]>':
            post(token=token, doc=doc)
            logout(token)
            return render_template("nice.html",
                                   the_title='Накладная отправлена')
        else:
            return render_template("error.html",
                                   ex=token,
                                   type_ex="Ошибка загрузки накладной, отправьте скриншот в поддержку")
    except Exception as ex:
        return render_template("error.html",
                               type_ex=ex.__class__,
                               ex=ex)


@app.route("/synch", methods=['post', 'get'])
def synch() -> 'html':
    try:
        synch_time = (str(datetime.now()))[0:-7]
        with open(Path(path_to_txt, 'synch.txt'), 'w', encoding=encod) as file:
            file.write(str(synch_time.replace(' ', 'T')))
        login = request.form['login']
        password = request.form['password']
        token = auth(login, password)
        all_write(token)
        logout(token)
        return render_template("nice.html",
                               the_title='Синхронизация выполнена')
    except Exception as ex:
        return render_template("error.html",
                               type_ex=ex.__class__,
                               ex=ex)


@app.route("/admin", methods=['post', 'get'])
def admin_page() -> 'html':
    try:
        return render_template("admin.html",
                               the_title="Настройки синхронизации с iiko",
                               protocol=protocol,
                               server=server,
                               port=port,
                               bd=bd,
                               days_per_order=days_per_order)
    except Exception as ex:
        return render_template("error.html",
                               type_ex=ex.__class__,
                               ex=ex)


@app.route("/admin_nice", methods=['post', 'get'])
def admin_page_2() -> 'html':
    try:
        if os.path.exists(Path(path_to_txt, 'category.txt')):
            clean_base()
        else:
            pass

        new_protocol = request.form['protocol']
        new_server = request.form['server']
        new_port = request.form['port']
        new_bd = request.form['bd']
        new_days_per_order = request.form['days_per_order']
        with open('variables.py', 'w', encoding=encod) as file:
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
    except Exception as ex:
        return render_template("error.html",
                               type_ex=ex.__class__,
                               ex=ex)


@app.route("/create", methods=["post", "get"])
def create_sample() -> 'html':
    try:
        with open(Path(path_to_samples, 'sample_list.txt'), encoding=encod) as file:
            sample_list = json.load(file)
    except FileNotFoundError:
        sample_list = []
    try:
        stocks_name = list(read_stocks().keys())
        suppliers_name = list(read_suppliers().keys())
        category_name = list(read_category().keys())
        category_name.append('Базовый прайс')
        return render_template('sample.html',
                               the_title="Шаблоны",
                               stocks_list=stocks_name,
                               suppliers_list=suppliers_name,
                               category_list=category_name,
                               sample_list=sample_list)
    except Exception as ex:
        return render_template("error.html",
                               type_ex=ex.__class__,
                               ex=ex)


@app.route("/create_sample", methods=["post", "get"])
def sample_create() -> 'html':
    try:
        global sample_stock, sample_supplier, sample_category, sample_pricelist, sample_name
        sample_stock = request.form['stock']
        sample_supplier = request.form['supplier']
        sample_category = request.form['categories']
        sample_name = request.form['sample_name']
        sample_pricelist = read_category_price(sample_category)
        order = list(sample_pricelist.keys())
        order.sort()
        return render_template("sample_complete.html",
                               the_title='Создание шаблона',
                               pricelist=sample_pricelist,
                               order=order)
    except Exception as ex:
        return render_template("error.html",
                               type_ex=ex.__class__,
                               ex=ex)


@app.route("/save_sample", methods=["post", "get"])
def save_sample() -> str:
    try:
        product_sample = list(sample_pricelist.keys())
        product_sample.sort()
        amount_sample = request.form.getlist('amount')
        print(amount_sample)
        sample_product_amount = dict(zip(product_sample, amount_sample))
        print(sample_product_amount)
        new_sample = {}
        for key, value in sample_product_amount.items():
            if value != 'on':
                continue
            else:
                new_sample[key] = value

        print(new_sample)
        file_sample = {
            'name': sample_name,
            'stock': sample_stock,
            'supplier': sample_supplier,
            'category': sample_category,
            'items': new_sample
        }
        with open(Path(path_to_samples, f'{sample_name}.json'), 'w', encoding=encod) as file:
            json.dump(file_sample, file, indent=4, ensure_ascii=False)

        if not os.path.exists(Path(path_to_samples, 'sample_list.txt')):
            sample_list = []
        else:
            with open(Path(path_to_samples, 'sample_list.txt'), 'r', encoding=encod) as file:
                sample_list = json.load(file)
        if sample_name not in sample_list:
            sample_list.append(sample_name)
        else:
            pass
        with open(Path(path_to_samples, 'sample_list.txt'), 'w', encoding=encod) as file:
            json.dump(sample_list, file, indent=4, ensure_ascii=False)
        return render_template("nice.html",
                               the_title=f'Шаблон {sample_name} сохранен')
    except Exception as ex:
        return render_template("error.html",
                               type_ex=ex.__class__,
                               ex=ex)


@app.route("/sample_send", methods=["post", "get"])
def sample_send() -> 'html':
    try:
        global sample_full, pricelist_sample
        sample = request.form['sample']
        if not os.path.exists(Path(path_to_samples, f'{sample}.json')):
            return render_template("error.html",
                                   ex='Такого шаблона нет в базе')
        else:
            with open(Path(path_to_samples, f'{sample}.json'), 'r', encoding=encod) as file:
                sample_full = json.load(file)
        pricelist_for_sample = read_category_price(sample_full['category'])
        pricelist_sample = {}
        for key, value in pricelist_for_sample.items():
            if key in list(sample_full['items'].keys()):
                pricelist_sample[key] = value
            else:
                continue
        pricelist_sample = dict(sorted(pricelist_sample.items()))
        all_price = 0
        for product, amount in sample_full['items'].items():
            all_price += float(pricelist_sample[product]) * float(amount)
        return render_template('sample_main_finally.html',
                               the_title="Проверка перед отправкой",
                               pricelist=pricelist_sample,
                               sample=sample_full,
                               all_price=all_price)
    except Exception as ex:
        return render_template("error.html",
                               type_ex=ex.__class__,
                               ex=ex)


@app.route("/send_2", methods=['post'])
def send_2() -> str:
    try:
        sample_date = request.form['date']
        sample_time = request.form['time']
        comment = request.form['comment-area']
        try_date = str(sample_date + 'T' + sample_time + ':00')
        sample_amountlist = dict(zip(list(pricelist_sample.keys()), list(sample_full['items'].values())))
        print(sample_amountlist)
        doc = data(sup=sample_full['supplier'],
                   stock=sample_full['stock'],
                   date=try_date,
                   pricelist=pricelist_sample,
                   amountlist=sample_amountlist,
                   comments=comment)
        login = request.form['login']
        password = request.form['password']
        token = auth(login, password)
        str_token = str(token)
        if str_token == '<Response [200]>':
            post(token=token, doc=doc)
            logout(token)
            return render_template("nice.html",
                                   the_title='Накладная отправлена')
        else:
            return render_template("error.html",
                                   ex=token,
                                   the_title="Ошибка загрузки накладной, отправьте скриншот в поддержку")
    except Exception as ex:
        return render_template("error.html",
                               type_ex=ex.__class__,
                               ex=ex)


# Запуск
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
