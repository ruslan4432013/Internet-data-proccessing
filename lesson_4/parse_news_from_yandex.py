"""
Написать приложение, которое собирает основные новости с сайта yandex-новости.
Для парсинга использовать XPath. Структура данных должна содержать:
название источника;
наименование новости;
ссылку на новость;
дата публикации.
Сложить собранные новости в БД
"""

import requests
from lxml import html
from datetime import datetime, timedelta
from pymongo import MongoClient


def to_date(date: list):
    date = date[0].split(' ')
    today = datetime.now().date()
    yesterday = (today - timedelta(days=1))
    if len(date) == 1:
        current_date = f'{today:%d.%m.%Y} {date[0]}'
    else:
        current_date = f'{yesterday:%d.%m.%Y} {date[-1]}'
    return current_date


def fill_mongo(data, data_base):
    contains = data_base.news.find_one({'link': data['link']})
    if not contains:
        data_base.news.insert_one(data)
        print('[INFO] Add news')


if __name__ == '__main__':
    # requests
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.174 YaBrowser/22.1.3.848 Yowser/2.5 Safari/537.36'}
    response = requests.get('https://yandex.ru/news/', headers=headers)


    # MongoDB setup
    client = MongoClient('localhost', 27017)
    db = client['news_data']

    # parse
    dom = html.fromstring(response.text)

    items = dom.xpath("//section[@aria-labelledby]//div[contains(@class, 'mg-card ')]")

    for item in items:
        root = response.url
        title = ''.join(item.xpath(".//h2[@class]/a/text()")).replace('\xa0', ' ')
        link = item.xpath(".//h2[@class]/a/@href")[0]
        date = to_date(item.xpath(".//*[@class='mg-card-source__time']/text()"))
        news_info = dict(root=root, title=title, link=link, date=date)
        fill_mongo(data=news_info, data_base=db)
