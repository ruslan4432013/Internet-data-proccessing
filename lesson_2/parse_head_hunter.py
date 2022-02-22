'''
Необходимо собрать информацию о вакансиях на вводимую должность
(используем input или через аргументы получаем должность)
с сайтов HH(обязательно) и/или Superjob(по желанию).
Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).
Получившийся список должен содержать в себе минимум:
Наименование вакансии.
Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
Ссылку на саму вакансию.
Сайт, откуда собрана вакансия.
По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
Сохраните в json либо csv.
'''

import json
import time
import asyncio
import aiohttp
from bs4 import BeautifulSoup

vacancy_data = []


async def get_page_data(session, page, text):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
    url = f'https://hh.ru/search/vacancy?fromSearchLine=true&text={text}&page={page}&hhtmFrom=vacancy_search_list'

    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()
        soup = BeautifulSoup(response_text, 'html.parser')

        vacancy_from_page = {'link_site': url, 'vacancy_list': []}
        articles = soup.find('div', {'class': 'vacancy-serp'})
        cart_articles = articles.children
        for cart in cart_articles:
            title = cart.find('a', {'class': 'bloko-link'})
            if hasattr(title, 'getText'):
                price = cart.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
                href = title.attrs.get('href')
                title = title.getText()

                if hasattr(price, 'getText'):
                    price = price.getText()
                    price = list(map(lambda x: x.strip(), price.replace('\u202f', '').split('–')))
                    price = list(map(lambda x: x.split(' '), price))
                    currency = price[0][-1] if len(price) == 1 else price[1][-1]
                    payment = {'currency': currency}
                    if 'от' in price[0]:
                        payment['min_pay'] = list(filter(lambda x: x.isdigit(), price[0]))[0]
                        payment['max_pay'] = 'Not specified'
                    elif 'до' in price[0]:
                        payment['min_pay'] = 'Not specified'
                        payment['max_pay'] = list(filter(lambda x: x.isdigit(), price[0]))[0]
                    elif len(price) == 2:
                        payment['min_pay'] = price[0][0]
                        payment['max_pay'] = price[1][0]
                else:
                    payment = {'min_pay': 'Not specified', 'currency': 'Not specified', 'max_pay': 'Not specified'}
                vacancy_info = {'title': title,
                                'payment': payment,
                                'link_vacancy': href}
                vacancy_from_page['vacancy_list'].append(vacancy_info)
        vacancy_data.append(vacancy_from_page)
        print(f'[INFO] Обработал страницу {page}')


async def gather_data(text):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
    url = f'https://hh.ru/search/vacancy?fromSearchLine=true&text={text}'

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)
        soup = BeautifulSoup(await response.text(), 'html.parser')
        pages_count = max([int(span.getText()) for span in soup.find('div', {'class': 'pager'}).find_all('span') if
                           span.getText().isdigit()])
        tasks = []
        for page in range(pages_count):
            task = asyncio.create_task(get_page_data(session, page, text=text))
            tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    loop = asyncio.get_event_loop()
    time.sleep(1)
    text = input('Введите желаемую вакансию: ')
    loop.run_until_complete(gather_data(text=text))
    # Получаемые данные
    with open('vacancy.json', 'w', encoding='utf-8') as f:
        json.dump(vacancy_data, f, ensure_ascii=False)
    print('Loading is done')


if __name__ == '__main__':
    main()
