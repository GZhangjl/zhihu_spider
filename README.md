# zhihu_spider

## 基本情况

* 知乎如果没有登陆，是无法访问所有问题与答案的，所以爬取知乎最初的一步就是如何使用账号密码完成模拟登陆；

* 首先想到的是使用`POST`请求，带上有账号密码信息的表单数据进行模拟登陆，但是据网友说这样做以前是可以的，但是目前已经不再允许，于是从便利性出发，依旧是使用`Selenium`进行模拟登陆；通过`Selenium`对[知乎登录页](https://www.zhihu.com/signin)进行模拟访问，识别网页中需要填入账号密码的表单进行传值，最后登陆，待登陆成功后，稍候几秒（使用`time.sleep`），进行`Cookie`的获取（以后便可以通过`Cookie`访问知乎）

* 成功登陆并获取`Cookie`后，便开始分析问题与答案的网页结构；问题的页面按照一般思路就能够获取并解析，只要从网页中提取出类似于 *https://www.zhihu.com/question/58978414* 这样的`URL`即可，可以不断从当前以及未来所有请求到的网页中获取该形式的`URL`，只要注意是否需要去重即可；通过浏览器进入问题页后会发现，每个问题在同一页面中默认显示的回答数量是有限的，可以通过滚动条下滑来加载更多的回答，所以无法通过静态网页的获取来提取回答的具体情况

* 通过查看浏览器开发者工具，发现一个`URL` [https://www.zhihu.com/api/v4/questions/589...&limit=5&offset=5&sort_by=default](https://www.zhihu.com/api/v4/questions/58978414/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit=5&offset=5&sort_by=default) ，该`URL`指向的其实是一个`Json`文件，通过将其内容复制出来发现该文件包括了相关问题中的5个回答，同时有`is_end`、`is_start`、`next`、`previous`、`totals`标签来指明“下一页”`URL`等信息，通过解析该`Json`文件就能够得到某一个问题下的所有回答信息

    > 知乎的问题和回答都是通过相应的`id`来确定的，只要观察相关`URL`的构造规律就能顺利某个问题与回答的相关页面

* 至此，页面分析工作基本完成，接下去进行数据库设计以及代码编写；该爬虫的`item`使用了`scrapy.loader.ItemLoader`进行额外封装，以方便进行页面解析以及数据处理，数据库使用`SQLAlchemy`库进行构建，为了面对问题和回答两种不同数据表结构复用同一套用于存储操作的`pipeline`，将各自数据表`model`和`model`的实例均嵌套在`item`类中，之后在`pipeline`中直接调用传递过来的`item`的方法或者嵌套类就能够完成数据表的创建和记录

* 以上基本完成对知乎问题以及回答的爬取，并且将结果保存到数据库中

### 完成改进

* 依旧是设定了`UserAgent`以及`proxy`，这定随机`UserAgent`值使用了`fake-useragent`包；因为前期已经发现[西刺代理（国内高匿代理）](http://www.xicidaili.com/nn)中存在大量无效`ip`，这次是通过`Scrapy`构建了`ip`爬虫，爬取西刺代理页面，并且在解析出结果后直接通过代理访问 *http://httpbin.org/ip* 网站；如果访问成功，将会返回对应`ip`值，如果`ip`无效，则会被网站拒绝，以此来验证爬到的`ip`是否能够使用；但是实际情况是，就算是通过爬取验证的代理最终也无法成功访问到知乎网站，故代理设置被搁置

* 当一个爬虫项目中存在两个爬虫（`zhihu_spider`/`proxies`）时，使用了`custom_settings`进行`settings`临时设置，这样可以实现同一个`settings`在两个爬虫中可以使用不同的`pipeline`与`middleware`

### 更新

* 同一个账号或者ip频繁访问知乎后，会被知乎判定为异常，请求被重定向到 *https://www.zhihu.com/account/unhuman?type=unhuman&message=...&need_login=false* 这样一个URL，需要输入验证码才能继续；从实际运行情况来看，如果在被知乎阻碍的情况下再一次运行Selenium进行模拟登陆，输入完账号密码后就会直接跳转到输验证码页面，代码更新后，在此时会在操作台中打印提示信息，然后提取验证码图片并进行输入（由于云打码平台需要收费，暂时使用`input`来手工打码）来通过验证，之后将跳转至正常首页。

* 在爬虫过程中出现需要验证码验证的情况暂时没碰到，暂时无法分析页面的具体情况，所以暂时未作出具体处理。

* 最近接触到第三方GUI库[`PySimpleGUI`](https://github.com/MikeTheWatchGuy/PySimpleGUI)，所以尝试使用该库制作了一个小的对话框，会在知乎检测到异常后跳出用于显示验证码和手工输入确认，虽然从功能上来说依旧鸡肋，但是比之前在操作台中输入要优雅一下（2018-08-29）
![image](https://github.com/GZhangjl/zhihu_spider/blob/master/captcha_input.png)

* 更新代码，依旧是验证码处理，添加了[`云打码`](http://yundama.com/)平台的接入（ **由于之前接触过，所以使用了该平台，该平台或者其他打码平台如何使用详见各自官网** ），可以通过云打码用户进行验证码识别（平台是收费的）；由于 **收费** 属性，所以该部分代码默认已经被注释；使用前除了解除注释，还需要在`settings`文件中设置云打码平台账号密码，云打码接口脚本放在`utils`文件夹下（2018-08-29）
