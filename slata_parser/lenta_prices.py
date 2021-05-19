import random
import time
from datetime import datetime
import requests
import xlsxwriter
from bs4 import BeautifulSoup
import re

# Ссылки для парсинга
LINKS = []

# Обход защиты: прикинуться браузером
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                         ' Chrome/86.0.4240.185 YaBrowser/20.11.2.78 Yowser/2.5 Safari/537.36', 'accept': '*/*'}


# Интервалы для таймаута между запросами по категориям
big_pauses = [30, 10, 22, 15, 15, 11, 20, 34]
small_pauses = [2, 1, 4, 2, 3, 5, 2, 1, 2]

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


# Создание списка ссылок на разделы каталога
def get_links_list(url):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a'):
        l = link.get('href')
        if '/catalog/' in str(l) and str(l) != '/catalog/':
            LINKS.append('https://lenta.com'+l)


# Запись результатов в exel
def exel(products_dict):
    cur_date = datetime.now().date().strftime('%d.%m.%Y')
    workbook = xlsxwriter.Workbook(f'{cur_date} Прайс-лист "Лента".xlsx')
    worksheet = workbook.add_worksheet()
    col_num = 0
    for key, value in products_dict.items():
        worksheet.write(0, col_num, key)
        worksheet.write_column(1, col_num, value)
        col_num += 1
    print(f'Создан файл {workbook.filename}')
    workbook.close()


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
    for line in LINKS:
        timeout = random.choice(big_pauses)
        print(f'Пожалуйста, подождите, у нас тайм-аут: {timeout}')
        time.sleep(timeout)
        print('Поехали дальше')
        try:
            print(f'Зашли на страницу {line}')
            html = get_html(line)
            if html.status_code == 200:
                pages_count = int(get_pages_count(html))
                print(f'Страница {line} имеет пагинатор {pages_count} страниц')
                for i in range(1, pages_count + 1):
                    timeout_min = random.choice(small_pauses)
                    print(f'Пожалуйста, подождите, у нас мини-тайм-аут: {timeout_min}')
                    time.sleep(timeout_min)
                    pages_url = f'{line}?page={i}'
                    print(f'Собираю цены на странице: {pages_url}')
                    pages_html = get_html(pages_url, params=None)
                    get_content(pages_html.text)
            else:
                print('Error')
        except Exception as e:
            print(f'Error: не могу открыть страницу {line}')


def run():
    # Получить актуальные разделы каталога
    get_links_list('https://lenta.com/catalog/')
    parse()
    exel(products_data)


if __name__ == '__main__':
    print('Поехали!')
    run()
    print('Программа выполнена')



