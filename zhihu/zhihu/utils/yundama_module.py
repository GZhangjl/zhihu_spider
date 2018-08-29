# 以下，经云打码平台Demo修改得到

import http.client, mimetypes, urllib, json, time, requests

from zhihu import settings

######################################################################

class YDMHttp:
    apiurl = 'http://api.yundama.com/api.php'
    username = ''
    password = ''
    appid = ''
    appkey = ''

    def __init__(self, username, password, appid, appkey):
        self.username = username
        self.password = password
        self.appid = str(appid)
        self.appkey = appkey

    def request(self, fields, files=None):
        if files is None:
            files = []
        response = self.post_url(self.apiurl, fields, files)
        response = json.loads(response)
        return response

    def balance(self):
        data = {'method': 'balance', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey}
        response = self.request(data)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['balance']
        else:
            return -9001

    def login(self):
        data = {'method': 'login', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey}
        response = self.request(data)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['uid']
        else:
            return -9001

    def upload(self, filename, codetype, timeout):
        data = {'method': 'upload', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'codetype': str(codetype), 'timeout': str(timeout)}
        file = {'file': filename}
        response = self.request(data, file)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['cid']
        else:
            return -9001

    def result(self, cid):
        data = {'method': 'result', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'cid': str(cid)}
        response = self.request(data)
        return response and response['text'] or ''

    def decode(self, filename, codetype, timeout):
        cid = self.upload(filename, codetype, timeout)
        if (cid > 0):
            for i in range(0, timeout):
                result = self.result(cid)
                if (result != ''):
                    return cid, result
                else:
                    time.sleep(1)
            return -3003, ''
        else:
            return cid, ''

    def report(self, cid):
        data = {'method': 'report', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'cid': str(cid), 'flag': '0'}
        response = self.request(data)
        if (response):
            return response['ret']
        else:
            return -9001

    def post_url(self, url, fields, files=None):
        if files is None:
            files = []
        for key in files:
            files[key] = open(files[key], 'rb');
        res = requests.post(url, files=files, data=fields)
        return res.text

######################################################################

def yundama_on(img_path, username=None, password=None):

    try:
        username = settings.yundama_username if username is None else username
        password = settings.yundama_password if password is None else password
    except AttributeError:
        pass
    finally:
        assert username and password, '请输入云打码用户账号密码，或在settings文件中设置账号密码'

    appid = 5667
    appkey = '24dc47d600175cb649fbd83aa25c396c'
    filename = img_path
    codetype = 1004
    timeout = 60

    yundama = YDMHttp(username, password, appid, appkey)
    yundama.login()
    _, result = yundama.decode(filename, codetype, timeout)

    return result

######################################################################

if __name__ == '__main__':

    print(yundama_on('./captcha.png')) # 输入保存下来的验证码图片路径

    # # 以下代码用于测试
    # # 用户名
    # username = '****'
    #
    # # 密码
    # password = '****'
    #
    # appid = 5667
    #
    # appkey = '24dc47d600175cb649fbd83aa25c396c'
    #
    # # 图片文件
    # filename = '******'
    #
    # # 验证码类型，# 例：1004表示4位字母数字，不同类型收费不同。请准确填写，否则影响识别率。在此查询所有类型 http://www.yundama.com/price.html
    # codetype = 1004
    #
    # # 超时时间，秒
    # timeout = 60
    #
    # # 检查
    # if (username == 'username'):
    #     print('请设置好相关参数再测试')
    # else:
    #     # 初始化
    #     yundama = YDMHttp(username, password, appid, appkey)
    #
    #     # 登陆云打码
    #     uid = yundama.login()
    #     print('uid: %s' % uid)
    #
    #     # 查询余额
    #     balance = yundama.balance()
    #     print('balance: %s' % balance)
    #
    #     # 开始识别，图片路径，验证码类型ID，超时时间（秒），识别结果
    #     cid, result = yundama.decode(filename, codetype, timeout)
    #     print('cid: %s, result: %s' % (cid, result))

######################################################################