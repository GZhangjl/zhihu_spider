# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, Join, TakeFirst
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, VARCHAR, TEXT, DATETIME, Boolean, TIMESTAMP
from datetime import datetime
from collections import defaultdict
# from time import localtime, strftime
# from sqlalchemy.orm import sessionmaker


engine = create_engine('mysql://root:root@localhost:3306/zhihu',echo=True)
Base = declarative_base()


class Question(Base):

    __tablename__ = 'zhihu_questions'

    id = Column(Integer, primary_key=True)
    url = Column(VARCHAR(200))
    title = Column(VARCHAR(300))
    content = Column(TEXT,nullable=True)
    topic = Column(String(100))
    answers_num = Column(Integer)
    follower = Column(Integer)
    watcher = Column(Integer)
    crawl_time = Column(DATETIME)


class Answer(Base):

    __tablename__ = 'zhihu_answers'

    q_id = Column(Integer)
    answer_id = Column(Integer,primary_key=True)
    author_id = Column(VARCHAR(100))
    author_name = Column(VARCHAR(100))
    author_is_advertiser = Column(Boolean)
    created_time = Column(DATETIME)
    updated_time = Column(DATETIME)
    voteup_num = Column(Integer)
    comment_num = Column(Integer)
    content = Column(TEXT)

# Session = sessionmaker(engine)
# session = Session()

def replace_str(value):
    return value.replace(",","")

def default_None():
    return None

class ZhihuQuestionItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    q_id = scrapy.Field(
        intput_processor = MapCompose(int),
        output_processor = TakeFirst()
    )
    q_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    q_title = scrapy.Field(
        output_processor=TakeFirst()
    )
    q_content = scrapy.Field(
        output_processor=TakeFirst()
    )
    q_topic = scrapy.Field(
        input_processor=Join("、"),
        output_processor=TakeFirst()
    )
    q_answers_num = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor = MapCompose(replace_str,int)
    )
    q_follower = scrapy.Field(
        input_processor=MapCompose(replace_str,int),
        output_processor=TakeFirst()
    )
    q_watcher = scrapy.Field(
        input_processor=MapCompose(replace_str,int),
        output_processor=TakeFirst()
    )
    crawl_time = scrapy.Field(
        output_processor=TakeFirst()
    )

    def member(self):

        question_dict = defaultdict(default_None,self)

        return Question(id=question_dict['q_id'],url=question_dict['q_url'],title=question_dict['q_title'],content=question_dict['q_content'],
                               topic=question_dict['q_topic'],answers_num=question_dict['q_answers_num'],follower=question_dict['q_follower'],
                               watcher=question_dict['q_watcher'],crawl_time=question_dict['crawl_time'])


class ZhihuAnswersItem(scrapy.Item):

    q_id = scrapy.Field()
    a_id = scrapy.Field()
    author_id = scrapy.Field()
    author_name = scrapy.Field()
    author_is_advertiser = scrapy.Field()
    a_created_time = scrapy.Field()
    a_updated_time = scrapy.Field()
    a_voteup_num = scrapy.Field()
    a_comment_num = scrapy.Field()
    a_content = scrapy.Field()

    def member(self):
        return Answer(q_id=int(self['q_id']),answer_id=int(self['a_id']),author_id=self['author_id'],author_name=self['author_name'],
                      author_is_advertiser=self['author_is_advertiser'],created_time=datetime.fromtimestamp(self['a_created_time']),
                      updated_time=datetime.fromtimestamp(self['a_updated_time']),voteup_num=self['a_voteup_num'],
                      comment_num=self['a_comment_num'],content=self['a_content'])