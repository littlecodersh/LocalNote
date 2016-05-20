import requests, getpass
from urllib import unquote

CONSUMER_KEY = 'littlecodersh1259'
CONSUMER_SECRET = '39cf81a16bcfb160'

def file_retry(n = 1):
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
    def __init__(self, consumerKey = CONSUMER_KEY, consumerSecret = CONSUMER_SECRET, sandbox = True, isInternational = False):
        if sandbox:
            self.host = 'sandbox.evernote.com'
        elif isInternational:
            self.host = 'app.evernote.com'
        else:
            self.host = 'app.yinxiang.com'
        self.consumerKey = consumerKey
        self.consumerSecret = consumerSecret
    def oauth(self):
        token = self.__get_tmp_token()
        if token is None: return
        account, password = self.__get_login_info()
        verifier = self.__get_ver(token, account, password)
        if verifier:
            return self.__get_token(token, verifier)
        else:
            return '', ''
    @file_retry(3)
    def __get_tmp_token(self):
        payload = {
            'oauth_callback': '127.0.0.1',
            'oauth_consumer_key': self.consumerKey,
            'oauth_signature': self.consumerSecret,
            'oauth_signature_method': 'PLAINTEXT',
        }
        r = requests.get('https://%s/oauth'%self.host, params = payload)
        return dict(item.split('=',1) for item in unquote(r.text).split('&')).get('oauth_token')
    def __get_login_info(self):
        account = raw_input('Username: ')
        password = getpass.getpass('Password: ')
        return account, password
    @file_retry(3)
    def __get_ver(self, token, account, password):
        access = {
            'authorize': 'Authorize',
            'oauth_token': token,
            'username': account,
            'password': password,
        }
        r = requests.post('https://%s/OAuth.action'%self.host, data = access)
        return dict(item.split('=', 1) for item in r.url.split('?')[-1].split('&')).get('oauth_verifier')
    @file_retry(3)
    def __get_token(self, token, verifier):
        payload = {
            'oauth_consumer_key': self.consumerKey,
            'oauth_token': token,
            'oauth_verifier': verifier,
            'oauth_signature': self.consumerSecret,
            'oauth_signature_method': 'PLAINTEXT',
        }
        r = requests.get('https://%s/oauth'%self.host, params = payload)
        return (dict(item.split('=',1) for item in unquote(r.text).split('&'))['oauth_token'],
            int(dict(item.split('=',1) for item in unquote(r.text).split('&'))['edam_expires']) / 1000)

if __name__=='__main__':
    print Oauth().oauth()
