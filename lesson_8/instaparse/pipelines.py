# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import hashlib
from scrapy.utils.python import to_bytes

import scrapy
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline


class InstaparsePipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instagram0204

    def process_item(self, item, spider):
        main_user = item.pop('main_user')
        followers = item.pop('followers')
        user_subscriptions_or_followers = f'{main_user}__followers' if followers else f'{main_user}__subscriptions'
        collection = self.mongo_base[user_subscriptions_or_followers]
        collection.insert_one(item)
        return item


class InstaPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        try:
            yield scrapy.Request(item['photo'])
        except Exception as e:
            print(e)

    def item_completed(self, results, item, info):
        if item.get('photo', None):
            item['photo'] = [itm[1] for itm in results if itm[0]][0]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        item_name = item['username'].replace('"', '')
        return f'{item_name}/{image_guid}.jpg'
