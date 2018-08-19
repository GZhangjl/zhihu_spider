# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

from .items import Base

temp_engine = 'mysql://{0}:{1}@{2}:{3}/{4}?charset=utf8'

class ZhihuPipeline(object):

    def __init__(self, eng):
        self.engine = create_engine(eng, echo=True)
        self.Session = sessionmaker(self.engine)

    def open_spider(self,spider):
        Base.metadata.create_all(self.engine)
        self.session = self.Session()

    def process_item(self, item, spider):
        one_item = item.member()
        # self.session.add(one_item)
        self.session.merge(one_item)
        self.session.commit()

    def close_spider(self,spider):
        self.session.close_all()

    @classmethod
    def from_crawler(cls, crawler):
        user = crawler.settings.get('User', 'root')
        passwd = crawler.settings.get('Passwd', 'root')
        host = crawler.settings.get('Host', 'localhost')
        port = crawler.settings.get('Port', '3306')
        dbname = crawler.settings.get('dbName', 'zhihu')
        eng = temp_engine.format(user, passwd, host, port, dbname)
        return cls(eng)


class ProxiesPipeline(object):

    proxies_dict = {'total': 0, 'proxies': {}}

    def process_item(self, item, spider):
        cls = self.__class__
        item_dict = dict(item)
        k, v = list(item_dict.items())[0]
        cls.proxies_dict['total'] += 1
        cls.proxies_dict['proxies'][k] = v

    def close_spider(self, spider):
        cls = self.__class__
        with open('./utils/proxies.json', 'w') as f:
            json.dump(cls.proxies_dict, f)