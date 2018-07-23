# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .items import Base


engine = create_engine('mysql://root:root@localhost:3306/zhihu?charset=utf8',echo=True)
Session = sessionmaker(engine)


class ZhihuPipeline(object):

    def open_spider(self,spider):
        Base.metadata.create_all(engine)
        self.session = Session()

    def process_item(self, item, spider):
        a = item.member()
        self.session.add(item.member())
        self.session.commit()
        pass

    def close_spider(self,spider):
        self.session.close_all()