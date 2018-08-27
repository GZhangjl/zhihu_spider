# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, Join, TakeFirst
# from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, DATETIME, BOOLEAN, NVARCHAR, MEDIUMTEXT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from collections import defaultdict
# from time import localtime, strftime
# from sqlalchemy.orm import sessionmaker



Base = declarative_base()

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

    class Question(Base):

        __tablename__ = 'zhihu_questions'

        id = Column(INTEGER(), primary_key=True)
        url = Column(VARCHAR(45))
        title = Column(NVARCHAR(100))
        content = Column(MEDIUMTEXT(), nullable=True)
        topic = Column(NVARCHAR(200))
        answers_num = Column(INTEGER())
        follower = Column(INTEGER())
        watcher = Column(INTEGER())
        crawl_time = Column(DATETIME())

    def member(self):
        cls = self.__class__
        q_dict = defaultdict(default_None,self)

        return cls.Question(id=q_dict['q_id'], url=q_dict['q_url'], title=q_dict['q_title'],
                            content=q_dict['q_content'], topic=q_dict['q_topic'], answers_num=q_dict['q_answers_num'],
                            follower=q_dict['q_follower'], watcher=q_dict['q_watcher'], crawl_time=q_dict['crawl_time'])


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

    class Answer(Base):

        __tablename__ = 'zhihu_answers'

        q_id = Column(INTEGER(), ForeignKey('zhihu_questions.id'))
        question = relationship('Question', backref='answer')
        answer_id = Column(INTEGER(), primary_key=True)
        author_id = Column(VARCHAR(100))
        author_name = Column(NVARCHAR(20))
        author_is_advertiser = Column(BOOLEAN())
        created_time = Column(DATETIME())
        updated_time = Column(DATETIME())
        voteup_num = Column(INTEGER())
        comment_num = Column(INTEGER())
        content = Column(MEDIUMTEXT())

    def member(self):
        cls = self.__class__

        return cls.Answer(q_id=int(self['q_id']),answer_id=int(self['a_id']),author_id=self['author_id'],author_name=self['author_name'],
                      author_is_advertiser=self['author_is_advertiser'],created_time=datetime.fromtimestamp(self['a_created_time']),
                      updated_time=datetime.fromtimestamp(self['a_updated_time']),voteup_num=self['a_voteup_num'],
                      comment_num=self['a_comment_num'],content=self['a_content'])