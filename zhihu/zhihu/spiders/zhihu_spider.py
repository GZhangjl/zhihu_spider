# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import Request
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags
import time
import re
import json
import datetime
from urllib import parse

from zhihu.items import ZhihuQuestionItem, ZhihuAnswersItem


class ZhihuSpiderSpider(scrapy.Spider):
    name = 'zhihu_spider'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    temp_answers_url = ['https://www.zhihu.com/api/v4/questions/{0}/answers?include=data[*].is_normal'
                        '%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail'
                        '%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment'
                        '%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission'
                        '%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt'
                        '%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp'
                        '%3Bdata[*].mark_infos[*].url%3Bdata[*].author.follower_count%2Cbadge[%3F(type%3Dbest'
                        '_answerer)].topics&limit={1}&offset={2}&sort_by=default']

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
    }

    # custom_settings = {
    #     'DOWNLOADER_MIDDLEWARES': {
    #        'zhihu.middlewares.ProxyDownloaderMiddleware': 543,
    #     }
    # }

    def parse(self, response):
        urls = response.css('a::attr(href)').extract()
        urls = [parse.urljoin(response.url,url) for url in urls]
        for url in urls:
            re_match = re.match('(https://www.zhihu.com/question/([0-9]+))/?.*', url)
            if re_match:
                question_url = re_match.group(1)
                question_id = re_match.group(2)
                yield Request(question_url, callback=self.parse_questions, headers=self.headers, meta={'question_id': question_id})
            else:
                yield Request(url, callback=self.parse, headers=self.headers)

    def parse_questions(self, response):
        q_item = ItemLoader(item=ZhihuQuestionItem(),response=response)
        q_id = response.meta['question_id']
        q_item.add_value('q_id', q_id)
        q_item.add_value('q_url', response.url)
        q_item.add_css('q_title', '.QuestionHeader-tags+h1::text')
        q_item.add_css('q_content', '.QuestionRichText.QuestionRichText--collapsed span::text')
        q_item.add_css('q_topic', '.Tag.QuestionTopic .Popover div::text')
        q_item.add_css('q_answers_num', '.List-headerText span::text')
        q_item.add_xpath('q_follower', '//div[@class="NumberBoard QuestionFollowStatus-counts NumberBoard--divider"]/button//strong/text()')
        q_item.add_xpath('q_watcher', '//div[@class="NumberBoard QuestionFollowStatus-counts NumberBoard--divider"]/div//strong/text()')
        q_item.add_value('crawl_time', datetime.datetime.now())
        question_item = q_item.load_item()

        answers_url = self.temp_answers_url[0].format(q_id, 15, 0)

        yield Request(url=answers_url, callback=self.parse_answers, headers=self.headers, meta={'q_id':q_id})

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
            answer_item['a_content'] = remove_tags(answer['content'], encoding='utf8')
            yield answer_item

        if answers_obj['paging']['is_end'] == 'false':
            next_url = answers_obj['paging']['next']
            yield Request(url=next_url, callback=self.parse_answers, headers=self.headers)

    def start_requests(self):
        from selenium import webdriver
        # 启动浏览器测试驱动
        # 原来是使用的最新版chrome以及最新版chromedriver会出现grant_type错误，经查为知乎开始在最近使用OAUTH认证。
        web_driver = webdriver.Chrome(r'C:\Users\zhang\Desktop\chromedriver_win32(1)\chromedriver.exe')
        web_driver.get('https://www.zhihu.com/signin')
        web_driver.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper input').send_keys(r'zhangjl_0912@163.com') # 输入账号
        web_driver.find_element_by_css_selector('.SignFlow-password input').send_keys(r'HJW13XD53zjl@#%W') # 输入密码
        web_driver.find_element_by_css_selector('[type=submit]').click()
        time.sleep(10)
        cookies = web_driver.get_cookies()
        web_driver.close()
        cookies_dict = {}
        for cookie in  cookies:
            cookies_dict[cookie['name']] = cookie['value']

        with open('./cookies/zhihu_cookies.json', 'w') as f:
            json.dump(cookies_dict, f)

        yield Request(url=self.start_urls[0], callback=self.parse, dont_filter=True, headers=self.headers, cookies=cookies_dict)
