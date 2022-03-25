from scrapy.crawler import CrawlerProcess
from leroymerlin_scraper import settings
from leroymerlin_scraper.spiders.leroymerlin import LeroymerlinSpider
from scrapy.settings import Settings

if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroymerlinSpider)
    process.start()