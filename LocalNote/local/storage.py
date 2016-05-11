import json, os, time, sys
from markdown2 import markdown
import chardet

from evernoteapi import EvernoteController

CONFIG_DIR = 'user.cfg'

# fileDictFormat: {
# 'notebookName':[('note1', timeStamp), ..],
# }
# fileFormat: {
# 'name': "note's name",
# 'content': u''.encode('utf-8'),
# 'attachment': [('name', u''.encode),..),],
# }

class Storage(object):
    def __init__(self):
        self.token, self.isSpecialToken, self.sandbox, self.isInternational, self.expireTime, self.lastUpdate = self.__load_config()
        self.encoding = sys.stdin.encoding
    def __load_config(self):
        if not os.path.exists(CONFIG_DIR): return '', None, None, None, 0, 0
        with open(CONFIG_DIR) as f: r = json.loads(f.read())
        return r.get('token', ''), r.get('is-special-token'), r.get('sandbox'), r.get('is-international'), r.get('expire-time', 0), r.get('last-update', 0)
    def __store_config(self):
        with open(CONFIG_DIR, 'w') as f:
            f.write(json.dumps({
                'token': self.token,
                'is-special-token': self.isSpecialToken,
                'sandbox': self.sandbox,
                'isInternational': self.isInternational,
                'expire-time': self.expireTime,
                'last-update': self.lastUpdate, }))
    def update_config(self, token=None, isSpecialToken=None, sandbox=None, isInternational=None, expireTime=None, lastUpdate=None):
        if not token is None: self.token = token
        if not isSpecialToken is None: self.isSpecialToken = isSpecialToken
        if not sandbox is None: self.sandbox = sandbox
        if not isInternational is None: self.isInternational = isInternational
        if not expireTime is None: self.expireTime = expireTime
        if not lastUpdate is None: self.lastUpdate = lastUpdate
        self.__store_config()
    def get_config(self):
        return self.token, self.isSpecialToken, self.sandbox, self.isInternational, self.expireTime, self.lastUpdate
    def __str_c2l(self, s):
        return s.decode('utf8').encode(sys.stdin.encoding)
    def __str_l2c(s):
        try:
            return s.decode(sys.stdin.encoding).encode('utf8')
        except:
            return s.decode(chardet.detect(s)['encoding'] or 'utf8').encode('utf8')
    def get_file(self, fileFullPath):
        try:
            with open(os.path.join(*[self.__str_c2l(p) for p in fileFullPath.split('/')])) as f: r = f.read()
            try:
                r.decode('utf8')
                return r
            except:
                try:
                    return r.decode(chardet.detect(r)).encode('utf8')
                except:
                    return
        except:
            return
    def write_file(self, fileFullPath, content, isMd):
        if 1 < len(fileFullPath.split('/')) and not os.path.exists(fileFullPath.split('/')[0]):
            os.mkdir(self.__str_c2l(fileFullPath.split('/')[0]))
        try:
            fileFullPath += '.md' if isMd else '.txt'
            with open(os.path.join(*fileFullPath.split('/')), 'wb') as f: f.write(content)
            return True
        except:
            return False
    def get_file_dict(self):
        fileDict = {}
        for nbName in os.walk('.').next()[1]:
            nbNameUtf8 = self.__str_l2c(nbName)
            fileDict[nbNameUtf8] = []
            for nName in reduce(lambda x,y: x+y, os.walk('.').next()[1:]):
                filePath = os.path.join(nbName, nName)
                if os.path.isdir(nName):
                    fileDict[nbNameUtf8].append((self.__str_l2c(nName), os.stat(filePath).st_mtime))
                else:
                    fileDict[nbNameUtf8].append((self.__str_l2c(os.path.splitext(nName)[0]), os.stat(filePath).st_mtime))
        return fileDict
