# zhihu_spider

## 基本情况

* 知乎如果没有登陆，则无法访问所有的问题与答案，所以爬取知乎问题、答案最初的一步就是如何使用账号密码完成模拟登陆；首先想到的是使用`POST`请求提交携带账号密码数据的表单数据进行模拟登陆，但是据网友说这样做以前是可以的，但是目前已经不再允许，所以自然而然依旧是`Selenium`进行模拟登陆

* 通过`Selenium`进行对[知乎登录页](https://www.zhihu.com/signin)进行模拟访问，抓取网页识别需要填入账号密码的表单进行传值，最后待登陆完成后，稍候5秒，进行`cookie`的获取（以后便可以通过`cookie`访问知乎页面）

* 登陆成功并能够获取`cookie`后，便需要开始分析问题与答案的网页结构；问题的页面按照一般思路就能够获取，只要从网页中提取出类似于 *https://www.zhihu.com/question/58978414* 这样的`URL`即可，可以不断从目前以及未来所有请求带的网页中获取该形式的`URL`，只要注意是否需要去重就行；
进入每个问题页后会发现，每个问题默认显示的回答是有限的，通过滚动条下滑会动态将其他回答加载到页面中，所以无法通过静态网页的获取来提取回答的情况

* 通过分析浏览器开发者工具，发现一个`URL` [https://www.zhihu.com/api/v4/questions/589...&limit=5&offset=5&sort_by=default](https://www.zhihu.com/api/v4/questions/58978414/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit=5&offset=5&sort_by=default) 指向的其实是一个`Json`文件，通过将内容复制出来发现该文件是包括了相关问题中的5个回答，但是有`next`、`previous`、`totals`标签来指明“下一页”的`URL`等信息

> 知乎的问题和回答都是通过相应的`id`来确定的，只要观察相关`URL`的构建规律就能顺利获得问题与回答的相关页面

* 至此，页面分析工作基本完成，接下去进行数据库设计以及代码编写；该爬虫的`item`使用了`scrapy.loader.ItemLoader`进行额外封装，以方便进行页面解析以及数据处理，数据库使用`SQLAlchemy`库进行构建，为了针对问题和回答不同的数据库复用同一套用于存储操作的`ZhihuPipeline`，将各自数据库`model`和`model`的实例均嵌套在`item`类中，之后在`pipeline`中直接调用实例方法或者嵌套类就能够完成数据表的创建和记录

* 以上就能够基本完成爬取知乎问题以及回答的过程并且将结果保存到数据库中

### 完成改进

* 依旧是设定了`UserAgent`以及`proxy`，`UserAgent`的操作依然是使用`fake-useragent`包，并且配合`middleware`；因为前期已经发现[西刺代理（国内高匿代理）](http://www.xicidaili.com/nn)中存在大量无效`ip`，这次是通过`Scrapy`构建`ip`爬虫，爬取西刺代理页面，并且在解析出结果后直接通过代理访问 *http://httpbin.org/ip* 网站，如果访问成功，将会返回对应`ip`，如果`ip`无效，则会被网站拒绝，以此来验证爬到的`ip`能够使用；但是实际情况是，就算是通过爬取验证的代理最终也无法成功访问到知乎网站，故代理设置又被搁置

* 当一个爬虫项目中存在两个爬虫（`zhihu_spider`/`proxies`）时，使用`custom_settings`进行`settings`临时设置，这样在两个爬虫的`pipeline`与`middleware`不同是可以相互区分
