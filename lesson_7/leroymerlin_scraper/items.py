# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst, Compose

def clear_price(value):
    value = int(value[0].replace(' ', ''))
    return value


def get_specifications(values):
    clear_main_values = [val for val in values if '\n' not in val]
    clear_sub_values = [val.replace('\n', '').replace(' ', '') for val in values if '\n' in val and val.replace('\n', '').replace(' ', '')]
    specifications = dict(zip(clear_main_values, clear_sub_values))
    return specifications

class LeroymerlinScraperItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=Compose(clear_price), output_processor=TakeFirst())
    specifications = scrapy.Field(input_processor=Compose(get_specifications), output_processor=TakeFirst())
