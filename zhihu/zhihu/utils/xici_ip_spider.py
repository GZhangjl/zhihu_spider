# -*- coding: utf-8 -*-

'''
本模块用Requests包对西刺代理网站的高匿ip进行爬取，然后通过接口为爬虫主体提交请求提供代理ip
这部分代理ip希望通过middleware加入request请求中。

未来希望能够用异步IO方法提高爬取速度
'''

import requests
from scrapy.selector import Selector
import json

headers = {
    'Host':'www.xicidaili.com',
    'Referer':'http://www.xicidaili.com/',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}

url = 'http://www.xicidaili.com/nn/{0}'

count = 0
proxy_dict = {
    'total':count,
    'proxy_storage':{}
}

able = []


for i in range(10):
    page = i + 1
    response = requests.get(url=url.format(page), headers=headers)
    ip_list = Selector(response=response).css('table tr')[1:]
    for ip_info in ip_list:
        if ip_info.css('td:nth-child(7)>div>div.slow'):
                # or ip_info.css('td:nth-child(6)::text').extract_first() == 'HTTPS':
            continue
        proxy_ip = ip_info.css('td:nth-child(2)::text').extract_first()
        proxy_port = ip_info.css('td:nth-child(3)::text').extract_first()
        proxy_http = ip_info.css('td:nth-child(6)::text').extract_first().lower()

        proxy = '{0}://{1}:{2}'.format(proxy_http, proxy_ip, proxy_port)

        # key = 'https' if 'https' in proxy else 'http'
        # proxies = {key: proxy}
        proxy_dict['proxy_storage'][count] = proxy
        count += 1

# l = len(able)

# def verifi_proxy(proxy):
#     key = 'http' if 'http' in proxy else 'https'
#     proxies = {key: proxy}
#     if requests.get(url='http://www.baidu.com', proxies=proxies, timeout=2).status_code == 200:
#         able.append(proxy)

proxy_dict['total'] = count

with open('./proxy.json', 'w') as f:
    json.dump(proxy_dict, f)