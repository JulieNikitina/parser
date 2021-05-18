import requests
from bs4 import BeautifulSoup

# Сервис для получения sitemap: https://vivazzi.pro/dev/site-urls/

# Страница с результатом поиска - списком sitemap (Запрос: slata.online)
url = 'https://vivazzi.pro/dev/site-urls/?site=slata.online&xml_url=sitemap.xml'

response = requests.get(url)
# Парсинг страницы с помощью библиотеки beautifulsoup
soup = BeautifulSoup(response.text, 'html.parser')
# Создание списка страниц для последующего парсинга и граббинга,
# поиск всех ссылок на странице
link_list = []
for link in soup.find_all('a'):
    l = link.get('href')
    # Критерий отбора нужных ссылок (Запрос: ссылки на каталог)
    if 'https://slata.online/catalog/' in l:
        link_list.append(l)

# Сохранение списка найденных страниц
with open('txt.txt', 'w') as file:
    for item in link_list:
        if 'https://slata.online/catalog/' in item:
            file.write("%s\n" % item)
