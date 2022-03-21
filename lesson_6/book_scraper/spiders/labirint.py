import scrapy
from scrapy.http import HtmlResponse
from book_scraper.items import BookScraperItem


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    counter = 1
    def __init__(self, mark):
        self.start_urls = [f'https://www.labirint.ru/search/{mark}/?stype=0&page=1']


    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@title='Следующая']/@href").get()
        self.counter += 1

        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = ['https://www.labirint.ru' + path for path in
                 response.xpath("//a[@class='product-title-link']/@href").getall()]

        for link in links:
            yield response.follow(link, callback=self.book_parse)

    def book_parse(self, response: HtmlResponse):
        url = response.url
        name = response.xpath("//div[@id='product-title']/h1//text()").get()

        authors = list(map(lambda x: x.replace('\n', ''), response.xpath("//div[@class='authors']//text()").getall()))
        author_dict = {}
        key = None
        for i, el in enumerate(authors):
            if ':' in el:
                key = el
            else:
                author_dict[key] = author_dict.get(key, []) + [el]


        old_price = response.xpath("//div[@class='buying-priceold-val']//text()").get()
        discount_price = list(
                            filter(
                                str.isdigit, response.xpath("//div[@class='buying-pricenew-val']//text()").getall()
                            )
                        )
        if discount_price:
            discount_price = discount_price[0]
        else:
            discount_price = None

        rating = response.xpath("//div[@id='rate']//text()").get()
        yield BookScraperItem(url=url,
                              name=name,
                              authors=author_dict,
                              price=old_price,
                              price_discount=discount_price,
                              rating=rating)
