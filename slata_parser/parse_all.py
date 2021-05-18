import requests
from bs4 import BeautifulSoup
import urllib.request

from requests.adapters import HTTPAdapter
from urllib3 import Retry

# Путь до награбленного
abs_path = '/Users/pikapichu/Documents/Python Work/slata_parser/imgs/'


# Чтение файла, содержащего список ссылок для граббинга
with open('links_list.txt') as file:
    lines = file.read().splitlines()
    # Retry - стратегия при неполучении ответа
    session = requests.Session()
    retry_strategy = Retry(total=5, backoff_factor=1)
    session.mount('https://', HTTPAdapter(max_retries=retry_strategy))
    for line in lines:
        try:
            response = session.get(line)
            print(f'Success: {line}')
            soup = BeautifulSoup(response.text, 'html.parser')
            try:
                # Поиск необходимых элементов на странице, после парсинга 
                # (Запрос: Ищем Артикул: "Арт", изображение товара 
                art = soup.find('div', class_='sku').find('span').text.replace('Арт. ', '')
                img = soup.find('div', class_='media product__image')
                title = soup.find('h1').text
                link = 'https:' + img.find('img').get('src')
                try:
                    # Скачивание файла 
                    s_img = urllib.request.urlopen(link, timeout=5).read()
                    out = open(f"{abs_path}{art}.jpg", "wb")
                    out.write(s_img)
                    out.close()
                # Логи для отслеживания процесса и отлова исключений
                except Exception as e:
                    print(f'Error: Нет картинки для артикула {art}, адрес: {link}')
            except Exception as e:
                print(f'Error: На странице нет Артикула')
        except Exception as e:
            print(f'Error: не могу открыть страницу {line}')
