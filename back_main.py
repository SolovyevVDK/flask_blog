import json
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

import functions
import hashlib
server_data = functions.read_server_data()
login = 'admin'  # Со страницы авторизации
password = 'restoRtest'  # Со страницы авторизации
token = functions.auth(login, password, server_data)  # Функция получения токена, написана в файле
print(functions.write_suppliers(token))
functions.logout(token, server_data)
