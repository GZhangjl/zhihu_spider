# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request


class ProxiesSpider(scrapy.Spider):
    name = 'proxies'
    allowed_domains = ['xicidaili.com']
    temp_url = 'http://www.xicidaili.com/nn/{0}'
    proxy_test_url = 'http://httpbin.org/ip'

    proxies_count = 0
    # proxies_dict = {'proxies':[]}

    headers = {
        'Host': 'www.xicidaili.com',
        'Referer': 'http://www.xicidaili.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }

    custom_settings = {
        'ITEM_PIPELINES': {
            'zhihu.pipelines.ZhihuPipeline': None,
            'zhihu.pipelines.ProxiesPipeline': 1,
        }
    }

    def start_requests(self):
        for i in range(1, 3):
            crawl_url = self.temp_url.format(i)

            yield Request(url=crawl_url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        ip_list = response.css('table tr')[1:]
        for ip_info in ip_list:
            if ip_info.css('td:nth-child(7)>div>div.slow'):
                continue
            proxy_ip = ip_info.css('td:nth-child(2)::text').extract_first()
            proxy_port = ip_info.css('td:nth-child(3)::text').extract_first()
            proxy_http = ip_info.css('td:nth-child(6)::text').extract_first().lower()

            proxy = '{0}://{1}:{2}'.format(proxy_http, proxy_ip, proxy_port)

            yield Request(url=self.proxy_test_url, meta={'proxy': proxy, 'ip_text': proxy_ip}, dont_filter=True, callback=self.test_parse)

    def test_parse(self, response):
        import json
        cls = self.__class__
        t = response.text
        t = json.loads(t)
        ip_text = response.meta['ip_text']
        proxy = response.meta['proxy']
        if ip_text == t['origin']:
            cls.proxies_count += 1
            yield {
                cls.proxies_count: proxy
            }