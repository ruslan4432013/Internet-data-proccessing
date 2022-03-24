from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor
from scrapy.utils.project import get_project_settings
from book_scraper.spiders.labirint import LabirintSpider
from book_scraper.spiders.book24 import Book24Spider

if __name__ == "__main__":
    mark = input('Введите желаемую книгу: ')
    configure_logging()
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    runner.crawl(LabirintSpider, mark=mark)
    runner.crawl(Book24Spider, mark=mark)
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())

    reactor.run()
