import sys,os
from scrapy.cmdline import execute


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# b = os.path.abspath(__file__)
# a = vars()
# a = sys.path

execute(['scrapy','crawl','zhihu_spider'])
# execute(['scrapy','crawl','proxies'])