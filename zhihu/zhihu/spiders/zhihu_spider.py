# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags
from selenium import webdriver
import time
import pickle
import re
import json
import datetime
from urllib import parse
from zhihu.items import ZhihuQuestionItem, ZhihuAnswersItem


class ZhihuSpiderSpider(scrapy.Spider):
    name = 'zhihu_spider'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    all_answers_url = ['https://www.zhihu.com/api/v4/questions/{0}/answers?include=data[*].is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata[*].mark_infos[*].url%3Bdata[*].author.follower_count%2Cbadge[%3F(type%3Dbest_answerer)].topics&limit={1}&offset={2}&sort_by=default']

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
    }

    def parse(self, response):
        url_all = response.css('a::attr(href)').extract()
        url_all = [parse.urljoin(response.url,url) for url in url_all]
        for url in url_all:
            re_match = re.match('(https://www.zhihu.com/question/([0-9]+))/?.*',url)
            if re_match:
                question_url = re_match.group(1)
                question_id = re_match.group(2)
                yield Request(question_url,callback=self.parse_question,headers=self.headers,meta={'question_id':question_id})
            else:
                yield Request(url,callback=self.parse,headers=self.headers)


    def parse_question(self,response):
        q_item = ItemLoader(item=ZhihuQuestionItem(),response=response)
        q_item.add_value('q_id',response.meta['question_id'])
        q_item.add_value('q_url',response.url)
        q_item.add_css('q_title','.QuestionHeader-tags+h1::text')
        q_item.add_css('q_content','.QuestionRichText.QuestionRichText--collapsed span::text')
        q_item.add_css('q_topic','.Tag.QuestionTopic .Popover div::text')
        q_item.add_css('q_answers_num','.List-headerText span::text')
        q_item.add_xpath('q_follower','//div[@class="NumberBoard QuestionFollowStatus-counts NumberBoard--divider"]/button//strong/text()')
        q_item.add_xpath('q_watcher','//div[@class="NumberBoard QuestionFollowStatus-counts NumberBoard--divider"]/div//strong/text()')
        q_item.add_value('crawl_time',datetime.datetime.now())

        question_item = q_item.load_item()

        answers_url = self.all_answers_url[0].format(response.meta['question_id'],10,0)
        q_id = response.meta['question_id']

        yield Request(url=answers_url,callback=self.parse_answers,headers=self.headers,meta={'q_id':q_id})

        yield question_item


    def parse_answers(self,response):
        answers_obj = json.loads(response.text)

        for answer in answers_obj['data']:

            answer_item = ZhihuAnswersItem()
            answer_item['q_id'] = response.meta['q_id']
            answer_item['a_id'] = answer['id']
            answer_item['author_id'] = answer['author']['id'] if answer['author']['id'] != '0' else None
            answer_item['author_name'] = answer['author']['name']
            answer_item['author_is_advertiser'] = answer['author']['is_advertiser']
            answer_item['a_created_time'] = answer['created_time']
            answer_item['a_updated_time'] = answer['updated_time']
            answer_item['a_voteup_num'] = answer['voteup_count']
            answer_item['a_comment_num'] = answer['comment_count']
            answer_item['a_content'] = remove_tags(answer['content'],encoding='utf8')

            yield answer_item

        if answers_obj['paging']['is_end'] == 'false':
            next_url = answers_obj['paging']['next']
            yield Request(url=next_url,callback=self.parse_answers,headers=self.headers)


    def start_requests(self):
        #启动浏览器测试驱动
        # web_driver = webdriver.Chrome('C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe')
        # web_driver.get('https://www.zhihu.com/signin')
        # web_driver.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper input').send_keys('zhangjl_0912@163.com')
        # web_driver.find_element_by_css_selector('.SignFlow-password input').send_keys('HJW13XD53zjl')
        # web_driver.find_element_by_css_selector('[type=submit]').click()
        #
        # time.sleep(10)
        #
        # cookies = web_driver.get_cookies()
        # cookies_dict = {}
        #
        # for cookie in  cookies:
        #     f = open('C:/Users/zhang/Desktop/zhihu_spider/zhihu/zhihu/cookie/' + 'cookies.zhihu','wb')
        #     pickle.dump(cookie,f)
        #     cookies_dict[cookie['name']] = cookie['value']
        #
        # web_driver.close()

        cookies_dict = {'tgw_l7_route': 'b3dca7eade474617fe4df56e6c4934a3', 'z_c0': '"2|1:0|10:1532309009|4:z_c0|92:Mi4xOW1uX0FBQUFBQUFBVUtldHBVTHhEU1lBQUFCZ0FsVk5FSHhDWEFDdWt3VmFlZUkyWHVZUVQ1Q1g3TXI0a1EteTRB|010d9ff20a15d2b2c138559450405fc5e116092c807ef011102f541569fb6712"', 'q_c1': 'dc439125aa224c17a98650682d87b56f|1532309006000|1532309006000', '_zap': '8becb406-a5de-4eae-86e6-e80a3b91ee99', 'd_c0': '"AFCnraVC8Q2PTvPs6nMYaGqL6TI_op5t7Qo=|1532309006"', '_xsrf': 'f1c78012-2459-4985-8bf0-e4f76764f042', 'capsion_ticket': '"2|1:0|10:1532309007|14:capsion_ticket|44:MTI2ZTc3MzY3MzI5NGQ1MDk1NWRjMzFjOTNmNDE3Y2Y=|f6d8caaa1082b60f0148c443f736c87404b20a860a229017e13bf5bbbaa8c392"'}
        yield scrapy.Request(url=self.start_urls[0],callback=self.parse,headers=self.headers,dont_filter=True,cookies=cookies_dict)