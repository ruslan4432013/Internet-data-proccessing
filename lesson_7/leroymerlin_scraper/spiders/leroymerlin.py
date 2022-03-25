import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader

from leroymerlin_scraper.items import LeroymerlinScraperItem


class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = ['https://leroymerlin.ru/catalogue/kuhni/']

    def parse(self, response: HtmlResponse, **kwargs):
        next_page = response.xpath("//a[@data-qa-pagination-item='right']")[0]
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[@data-qa='product-name']")

        for link in links:
            yield response.follow(link, callback=self.parse_item)


    def parse_item(self, response):
        loader = ItemLoader(item=LeroymerlinScraperItem(), response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('name', "//h1[@class='header-2']/text()")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('photos', "//picture[@slot='pictures']/source[1]/@srcset")
        loader.add_xpath('specifications', "//div[@class='def-list__group']//text()")
        yield loader.load_item()
