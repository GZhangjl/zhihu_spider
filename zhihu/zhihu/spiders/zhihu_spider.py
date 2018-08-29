# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import Request, HtmlResponse
from scrapy.loader import ItemLoader
import logging
from w3lib.html import remove_tags
import time
import re
import json
import datetime
from urllib import parse

# from zheye import zheye
from zhihu.items import ZhihuQuestionItem, ZhihuAnswersItem

loger = logging.getLogger('Spider')

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
        # 原来是使用的最新版chrome以及最新版chromedriver会出现grant_type错误，经查为知乎开始在最近使用OAuth认证。经测试，暂时较低
        # 版本的chrome以及相应驱动可以运行
        web_driver = webdriver.Chrome(r'C:\Users\zhang\Desktop\chromedriver_win32\chromedriver.exe', )
        web_driver.get('https://www.zhihu.com/signin')
        web_driver.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper input').send_keys('****') # 输入账号
        web_driver.find_element_by_css_selector('.SignFlow-password input').send_keys('****') # 输入密码

        # 网上普遍的声音是既然已经在使用Selenium了，那这些难办的验证码（这里指比如倒立文字验证码）直接预留时间手工点就行了
        # 原来有设想将开源第三方库zheye接入spider，但是在Selenium下很难做到，同时在有浏览器界面的情况下也显得没有必要
        time.sleep(5) # 给出等待时间用于处理可能存在的验证码，一般如果账号密码正确即可一次登录成功不会显示验证码
        web_driver.find_element_by_css_selector('[type=submit]').click()
        time.sleep(5)

        # “系统检测到您的帐号或IP存在异常流量，请进行验证用于确认这些请求不是自动程序发出的”
        # 在同一ip（或同一账号）频繁访问知乎后，会被检测到疑似爬虫，需要验证码确认，以下为在模拟登陆后就出现验证码确认的情况的处理代码
        try:
            warn = web_driver.find_element_by_css_selector('.Unhuman-tip').text
        except:
            loger.debug('未检测出异常')
        else:
            loger.debug("CAPTCHA WARNING:{warn}".format(warn=warn))
            page_html = web_driver.page_source
            xpath_str = '//*[@id="root"]/div/div[2]/section/div/img/@src'
            # 这里使用PySimpleGUI库做了一个小的界面，能够直接弹出对话框来进行验证码输入，虽然依然鸡肋，但是跟之前往console中输入相比更加优雅一点
            captcha_text = self.input_captcha('zhihu.com', page_html, xpath_str)
            web_driver.find_element_by_css_selector('div.Unhuman-input>input').send_keys(captcha_text)
            web_driver.find_element_by_css_selector('section.Unhuman-verificationCode>button').click()

        time.sleep(10)
        cookies = web_driver.get_cookies()
        web_driver.close()
        cookies_dict = {}
        for cookie in  cookies:
            cookies_dict[cookie['name']] = cookie['value']

        with open('./cookies/zhihu_cookies.json', 'w') as f:
            json.dump(cookies_dict, f)

        yield Request(url=self.start_urls[0], callback=self.parse, dont_filter=True, headers=self.headers, cookies=cookies_dict)

    # 该方法主要用于爬虫被检测到后验证码页面的解析和操作
    def input_captcha(self, url, body_str, xpath_str):
        from base64 import b64decode
        # from PIL import Image
        from zhihu.utils.captcha_input import captcha_input
        html_response = HtmlResponse(url=url, body=body_str, encoding='utf8')
        captcha_uri = html_response.xpath(xpath_str).extract_first()
        captcha = b64decode(captcha_uri.replace('\n', '').partition(',')[-1])

        with open('./utils/captcha.png','wb') as img:
            img.write(captcha)

        return captcha_input('./utils/captcha.png')

        # 以下代码是原来用于往console中输入验证码的代码

        # 由于云打码的接入可能需要收费，所以暂时使用了自动显示验证码图片，然后可以手工往Console输入验证码的方式进行（虽然这样做跟直接在
        # 模拟浏览器中直接输入验证码没区别）

        # with Image.open('./utils/captcha.png') as img:
        #     img.show()
        #
        # captcha_text = input('请输入显示验证码：')
        #
        # return captcha_text