# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparseItem(scrapy.Item):
    _id = scrapy.Field()
    main_user = scrapy.Field()
    followers = scrapy.Field()
    username = scrapy.Field()
    full_name = scrapy.Field()
    user_id = scrapy.Field()
    photo = scrapy.Field()

