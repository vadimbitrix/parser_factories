import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd

# Константа для тестирования
TEST_PAGES = 10  # установите значение 0 для обработки всех страниц

# Время начала работы скрипта
start_time = time.time()

def format_elapsed_time(seconds):
    """Форматирует прошедшее время в удобный вид."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{int(hours)} часов {int(minutes)} минут {int(seconds)} секунд"
    elif minutes:
        return f"{int(minutes)} минут {int(seconds)} секунд"
    else:
        return f"{int(seconds)} секунд"

def parse_detail_page(url):
    time.sleep(random.uniform(2, 4))  # задержка перед каждым запросом
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.content, 'html.parser')

    # Извлекаем регион и город
    breadcrumbs = soup.find('ul', class_='breadCrumbs').find_all('li')
    region = ''
    city = ''
    if len(breadcrumbs) >= 5:  # Убедимся, что есть достаточно элементов
        region = breadcrumbs[2].text
        city = breadcrumbs[3].text

    # Извлекаем название завода
    name = soup.find('h1').text
    current_time = time.time()
    elapsed_time = format_elapsed_time(current_time - start_time)
    print(f'Парсим завод {name}... Прошло времени: {elapsed_time}')

    # Извлекаем контактные данные
    contacts = soup.find('div', id='contact-company').find_all('li')
    phone_numbers = []
    email = ''
    website = ''
    for contact in contacts:
        title = contact.find('span', class_='content-list__title').text
        if 'Телефон' in title:
            phone_divs = contact.find_all('div')
            for div in phone_divs:
                phone_number = div.find('a').text.strip()
                phone_numbers.append(phone_number)
        elif 'Эл. почта' in title:
            email = contact.find('a')['href'].replace('mailto:', '')
        elif 'Сайт' in title:
            website = contact.find('a')['href']
    phone = ', '.join(phone_numbers)

    # Формируем и возвращаем словарь с данными
    return {
        'Название': name,
        'Телефон': phone,
        'Город': city,
        'Регион': region,
        'Email': email,
        'Сайт': website,
        'Ссылка': url
    }


def parse_page(url):
    time.sleep(random.uniform(2, 4))  # задержка перед каждым запросом
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()  # проверка на ошибки
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    factories = soup.find_all('div', class_=['factory', 'teaser'])  # ищем все блоки с заводами

    data = []
    for factory in factories:
        title_tag = factory.find('a', class_='factory__title')  # ищем тег с названием завода
        if title_tag:
            title = title_tag.text
            link = title_tag['href']
            data.append((title, f'https://xn--80aegj1b5e.xn--p1ai{link}'))  # сохраняем данные

    return data

def parse_all_pages(base_url, pages):
    all_data = []
    max_pages = TEST_PAGES if TEST_PAGES > 0 else pages
    for page in range(1, max_pages + 1):
        current_time = time.time()
        elapsed_time = format_elapsed_time(current_time - start_time)
        url = f'{base_url}?page={page}'
        print(f'Парсим ссылки на заводы из страницы {page}... {url} Прошло времени: {elapsed_time}')
        try:
            all_data.extend(parse_page(url))
        except Exception as err:
            print(f'An error occurred: {err}')

    return all_data


if __name__ == "__main__":
    base_url = 'https://xn--80aegj1b5e.xn--p1ai/factories'
    pages = 1033  # измените это значение в зависимости от количества страниц на сайте
    all_factories_data = parse_all_pages(base_url, pages)
    detailed_data = [parse_detail_page(url[1]) for url in all_factories_data]

    # Экспорт данных в Excel
    df = pd.DataFrame(detailed_data)
    df.to_excel('factories_data.xlsx', index=False)
