import random
import time

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

LINES = [
    'https://lenta.com/catalog/hleb-i-hlebobulochnye-izdeliya/'
]

# Путь до сохраняемого файла
file_path = './result_price.xlsx'

# Обход защиты: прикинуться браузером
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                         ' Chrome/86.0.4240.185 YaBrowser/20.11.2.78 Yowser/2.5 Safari/537.36', 'accept': '*/*'}

# Интервалы для таймаута между запросами по категориям
times = [30, 10, 22, 15, 15, 11, 20, 34]

# Исходники для создания словаря с полученными данными,
# которые будут выгружены в xlsx-файл
titles = []
reg_prices = []
card_prices = []
products_data = {
    "Наименование": titles,
    "Обычная цена": reg_prices,
    "Цена по карте": card_prices
}


#  Запись полученных данных в xlsx-файл
def write_exel(data):
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    print('Документ собрался')


# Создание списка ссылок на разделы каталога
def get_links_list(url):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    link_list = []
    for link in soup.find_all('a'):
        l = link.get('href')
        if '/catalog/' in str(l):
            link_list.append(l)
    with open('list.txt', 'w') as file:
        for item in link_list:
            file.write("%s\n" % ('https://lenta.com' + item))


# Получение количества страниц пагинации в разделе
def get_pages_count(html):
    soup = BeautifulSoup(html.text, 'html.parser')
    pagination = soup.find('ul', class_='pagination').find('li', class_='next').find('a').get('rel')
    return pagination[2]


def get_html(url, params=None):
    try:
        r = requests.get(url, headers=HEADERS, params=params)
        return r
    except Exception as e:
        print(f'не могу получить html {url}')


# Функция поиска необходимых данных на странице
def get_content(html):
    # Регулярка для получения числа-цены, без лишних знаков
    REG = '^\s+|\n|\r|\s+$'
    try:
        soup = BeautifulSoup(html, 'html.parser')
        objects = soup.find_all('div', class_='sku-card-small-container')
        for obj in objects:
            # Название продукта
            title = obj.find('div', class_='sku-card-small__title').text
            title = re.sub(REG, '', title)
            titles.append(title)
            # Стоимость без карты клиента
            price_reg = obj.find('div',
                                 class_="sku-price sku-price--regular sku-price--small sku-prices-block__price").find(
                'span', class_='sku-price__integer').text
            price_reg = re.sub(REG, '', price_reg)
            reg_prices.append(price_reg)
            # Стоимость с картой клиента
            price_card = obj.find('div',
                                  class_="sku-price sku-price--primary sku-price--small sku-prices-block__price").find(
                'span', class_='sku-price__integer').text
            price_card = re.sub(REG, '', price_card)
            card_prices.append(price_card)
    except Exception as e:
        print(f'Не смог получить {html}')


# Запуск парсинга по страницам, указанным в файле-списке
def parse():
    # # with open('categories_list.txt') as file:
    # with open('links_list.txt') as file:
    #     lines = file.read().splitlines()
    #     for line in lines:
    for line in LINES:
        try:
            print(f'Зашли на страницу {line}')
            html = get_html(line)
            if html.status_code == 200:
                pages_count = int(get_pages_count(html))
                print(f'Страница {line} имеет пагинатор {pages_count} страниц')
                for i in range(1, pages_count + 1):
                    pages_url = f'{line}?page={i}'
                    print(f'Парсим {pages_url}')
                    pages_html = get_html(pages_url, params=None)
                    get_content(pages_html.text)
                timeout = random.choice(times)
                print(f'Начинаю таймаут {timeout}')
                time.sleep(timeout)
                print('Поехали дальше')
            else:
                print('Error')
        except Exception as e:
            print(f'Error: не могу открыть страницу {line}')


# print(products_data)
parse()
write_exel(products_data)

# Полусить актуальные разделы каталога
# get_links_list('https://lenta.com/catalog/')
