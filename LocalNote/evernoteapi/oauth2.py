#coding=utf8
import requests, re, sys, getpass, time

def retry(n = 1):
    def _file_retry(fn):
        def __file_retry(*args, **kwargs):
            for i in range(n):
                try:
                    return fn(*args, **kwargs)
                except:
                    pass
        return __file_retry
    return _file_retry

class Oauth(object):
    def __init__(self, sandbox = True, isInternational = False):
        if sandbox:
            self.host = 'https://sandbox.evernote.com'
        elif isInternational:
            self.host = 'https://www.evernote.com'
        else:
            self.host = 'https://app.yinxiang.com'
        self.s = requests.session()
    def oauth(self):
        preloadContent = self._pre_load()
        loginContent = self._login(preloadContent)
        if not 'Developer Tokens' in loginContent: return False, False
        return self.get_token(loginContent), time.time() + 31535000
    @retry(3)
    def _pre_load(self):
        return self.s.get(self.host + '/Login.action?targetUrl=%2Fapi%2FDeveloperToken.action').content
    @retry(3)
    def _login(self, preloadContent):
        data = {
            'username': raw_input('Username: ').decode(sys.stdin.encoding),
            'password': getpass.getpass(),
            'login': '登陆',
            'showSwitchService': 'true',
            'targetUrl': "/api/DeveloperToken.action",
            '_sourcePage': "MbulSL0GgBDiMUD9T65RG_YvRLZ-1eYO3fqfqRu0fynRL_1nukNa4gH1t86pc1SP",
            '__fp': "ZtDCgDFj-IY3yWPvuidLz-TPR6I9Jhx8",
        }
        for eid in ('hpts', 'hptsh'):
            data[eid] = re.compile('getElementById\("%s"\).value = "(.*?)";'%eid).search(preloadContent).groups()[0]
        return self.s.post(self.host + '/Login.action', data).content
    @retry(3)
    def get_token(self, loginContent):
        def _change_token(c, isCreated = False):
            dataTuple = ('secret', 'csrfBusterToken', '_sourcePage', '__fp')
            if isCreated:
                data = {'remove': 'Revoke your developer token', }
                dataTuple += ('noteStoreUrl',)
            else:
                data = {'create': 'Create a developer token', }
            for name in dataTuple:
                data[name] = re.compile('<input[^>]*?name="%s"[^>]*?value="(.*?)"'%name).search(c).groups()[0]
            return self.s.post(self.host + '/api/DeveloperToken.action', data).content
        if 'Your Developer Token has already been created' in loginContent: _change_token(loginContent, True)
        c = _change_token(loginContent)
        return re.compile('<input[^>]*?name="%s"[^>]*?value="(.*?)"'%'accessToken').search(c).groups()[0]

if __name__ == '__main__':
    print Oauth().oauth()
