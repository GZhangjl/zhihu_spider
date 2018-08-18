# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy.orm import sessionmaker

from .items import Base, engine

Session = sessionmaker(engine)


class ZhihuPipeline(object):

    def open_spider(self,spider):
        Base.metadata.create_all(engine)
        self.session = Session()

    def process_item(self, item, spider):
        one_item = item.member()
        # self.session.add(one_item)
        self.session.merge(one_item)
        self.session.commit()

    def close_spider(self,spider):
        self.session.close_all()