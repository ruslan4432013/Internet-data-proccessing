'''
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
которая будет добавлять только новые вакансии/продукты в вашу базу.
2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы
(необходимо анализировать оба поля зарплаты).
'''
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient


class WebScraper:

    def __init__(self, need_scrub=True):
        self.vacancy = WebScraper.setup_mongo_client()
        self.need_scrub = need_scrub
        if self.need_scrub:
            self.vacancy_data = []
            self.text = input('Введите желаемую вакансию: ')
            self.url = f'https://hh.ru/search/vacancy?fromSearchLine=true&text={self.text}&items_on_page=20&area=1'
            self.headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
            self.max_page = self.get_max_page()
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.gather_data())
            print(f'[INFO] Вакансии получены')
            print(f'[INFO] Вакансии загружаются')
            self.__fill_mongo()
            print('Вакансии вставлены в базу данных')

    async def get_page_data(self, session, page):

        url = f'https://hh.ru/search/vacancy?fromSearchLine=true&text={self.text}&page={page}&hhtmFrom=vacancy_search_list&items_on_page=20&area=1'

        async with session.get(url=url, headers=self.headers) as response:
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
                            payment['min_pay'] = int(list(filter(lambda x: x.isdigit(), price[0]))[0])
                            payment['max_pay'] = None
                        elif 'до' in price[0]:
                            payment['min_pay'] = None
                            payment['max_pay'] = int(list(filter(lambda x: x.isdigit(), price[0]))[0])
                        elif len(price) == 2:
                            payment['min_pay'] = int(price[0][0])
                            payment['max_pay'] = int(price[1][0])
                    else:
                        payment = {'min_pay': None, 'currency': None, 'max_pay': None}
                    vacancy_info = {'title': title,
                                    'payment': payment,
                                    'link_vacancy': href}
                    vacancy_from_page['vacancy_list'].append(vacancy_info)
            self.vacancy_data.append(vacancy_from_page)
            print(f'[INFO] Обработал страницу {page}')

    async def gather_data(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for page in range(self.max_page):
                task = asyncio.create_task(self.get_page_data(session, page))
                tasks.append(task)
            await asyncio.gather(*tasks)

    def get_max_page(self):
        response = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        pages_count = max([int(span.getText()) for span in soup.find('div', {'class': 'pager'}).find_all('span') if
                           span.getText().isdigit()])
        return pages_count

    def __fill_mongo(self):
        for vacancy in self.vacancy_data:
            for data in vacancy['vacancy_list']:
                title = data['title']
                link = data['link_vacancy']
                contains = self.vacancy.find_one({'$and': [{'title': title}, {'link_vacancy': link}]})
                if not contains:
                    self.vacancy.insert_one(data)

    def search_in_mongo(self, min_pay):
        result = self.vacancy.find(
            {'$or': [{'payment.min_pay': {'$gte': min_pay}}, {'payment.max_pay': {'$gte': min_pay}}]})
        for vacancy in result:
            print(vacancy)

    @classmethod
    def setup_mongo_client(cls):
        client = MongoClient('localhost', 27017)
        db = client['vacancy_data']
        return db.vacancy


def main():
    parser = WebScraper(need_scrub=False)

    print('Поиск по минимальной заработной плате')
    min_pay = 200000
    parser.search_in_mongo(min_pay)


if __name__ == '__main__':
    main()
