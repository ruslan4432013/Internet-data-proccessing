import scrapy
from scrapy.http import HtmlResponse
from book_scraper.items import BookScraperItem


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']

    counter = 2
    def __init__(self, mark):
        self.mark = mark
        self.start_urls = [f'https://book24.ru/search/page-1/?q={mark}&available=2']


    def parse(self, response: HtmlResponse):
        next_page = f'https://book24.ru/search/page-{self.counter}/?q={self.mark}&available=2'
        self.counter += 1
        if response.status == 200:
            yield response.follow(next_page, callback=self.parse)
            links = ['https://book24.ru' + link for link in response.xpath("//a[contains(@class,'product-card__name')]//@href").getall()]
            for link in links:
                yield response.follow(link, callback=self.book_parse)

    def book_parse(self, response: HtmlResponse):

        url = response.url
        name = response.xpath("//h1[@itemprop='name']//text()").get()
        authors = response.xpath("//div[@class='product-characteristic__item']//text()").getall()[1:]
        author_dict = {}
        for author in authors:
            if ':' not in author:
                author_dict['authors'] = author_dict.get('authors', []) + [author]
            else:
                break

        old_price = response.xpath("//span[@class='app-price product-sidebar-price__price-old']//text()").getall()
        if old_price and isinstance(old_price, list):
            old_price = old_price[0].replace("\xa0", "").replace(' ', '')
        discount_price = response.xpath(
            "//span[@class='app-price product-sidebar-price__price']//text()").get().replace("\xa0", "").replace(' ', '')
        if not old_price:
            old_price = discount_price
            discount_price = None

        rating = response.xpath("//span[@class='rating-widget__main-text']//text()").get().replace(' ', '')
        yield BookScraperItem(url=url,
                              name=name,
                              authors=author_dict,
                              price=old_price,
                              price_discount=discount_price,
                              rating=rating)