import json, os, time, sys
from markdown2 import markdown
import chardet

from evernoteapi import EvernoteController

CONFIG_DIR = 'user.cfg'

class Storage(object):
    def __init__(self):
        self.token, self.isSpecialToken, self.sandbox, self.isInternational, self.expireTime, self.lastUpdate = self.__load_config()
        self.available, self.ec = self.__check_available()
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
    def __check_available(self):
        if not self.isSpecialToken and self.expireTime < time.time(): return False, None
        if self.token == '': return False, None
        try:
            ec = EvernoteController(self.token, self.isSpecialToken, self.sandbox, self.isInternational)
            self.__store_config()
            return True, ec
        except:
            return False, None
    def update_config(self, token=None, isSpecialToken=None, sandbox=None, isInternational=None, expireTime=None, lastUpdate=None):
        if not token is None: self.token = token
        if not isSpecialToken is None: self.isSpecialToken = isSpecialToken
        if not sandbox is None: self.sandbox = sandbox
        if not isInternational is None: self.isInternational = isInternational
        if not expireTime is None: self.expireTime = expireTime
        if not lastUpdate is None: self.lastUpdate = lastUpdate
        self.available, self.ec = self.__check_available()
    def download_file(self):
        if not self.available: return False
        for nbName, notebook in self.ec.storage.storage.items():
            if not os.path.exists(nbName): os.mkdir(self.__str_c2l(nbName))
            for nName, note in notebook.get('notes', {}).items():
                if not self.__check_file(nName, nbName, note) in (-1, 0): continue
                attachmentDict = self.ec.get_attachment('%s/%s'%(nbName, nName))
                if '%s.md'%nName in attachmentDict.keys():
                    with open(self.__str_c2l(os.path.join(nbName, '%s.md'%nName)), 'wb') as f:
                        f.write(attachmentDict['%s.md'%nName])
                else:
                    with open(self.__str_c2l(os.path.join(nbName, '%s.txt'%nName)), 'w') as f:
                        f.write(self.ec.get_content('%s/%s'%(nbName, nName)))
        self.lastUpdate = time.time() + 1 # in case chased by last file
        self.__store_config()
        return True
    def get_changes(self):
        r = '' # BUG: online delete
        if not self.available: return r
        for nbName, notebook in self.ec.storage.storage.items():
            if not os.path.exists(self.__str_c2l(nbName)):
                r += 'deleted %s/\n'%nbName
            else:
                for nName, note in notebook.get('notes', {}).items():
                    if not any(os.path.exists(self.__str_c2l(os.path.join(nbName, nName + postfix))) for postfix in ('.md', '.txt')):
                        r += 'deleted %s/%s\n'%(nbName, nName)
                    elif self.__check_file(nName, nbName, note) in (1, 0):
                        r += 'changed %s/%s\n'%(nbName, nName)
        return r
    def upload_file(self):
        if not self.available: return False
        for nbName, notebook in self.ec.storage.storage.items():
            if not os.path.exists(self.__str_c2l(nbName)):
                self.ec.delete_notebook(nbName)
            else:
                for nName, note in notebook.get('notes', {}).items():
                    if not any(os.path.exists(self.__str_c2l(os.path.join(nbName, nName + postfix))) for postfix in ('.md', '.txt')):
                        self.ec.delete_note('%s/%s'%(nbName, nName))
                    elif self.__check_file(nName, nbName, note) in (1, 0):
                        if os.path.exists(self.__str_c2l(os.path.join(nbName, nName + '.md'))):
                            content = self.__get_file_content(self.__str_c2l(os.path.join(nbName, nName + '.md')))
                            self.ec.update_note('%s/%s'%(nbName, nName), markdown(content).encode('utf8'), os.path.join(nbName, nName + '.md'))
                        elif os.path.exists(self.__str_c2l(os.path.join(nbName, nName + '.txt'))):
                            content = self.__get_file_content(self.__str_c2l(os.path.join(nbName, nName + '.txt')))
                            self.ec.update_note('%s/%s'%(nbName, nName), content)
        return True
    def __check_file(self, noteName, notebookName, note):
        # -1 for need download, 1 for need upload, 0 for can be uploaded and downloaded, 2 for updated
        if os.path.exists(self.__str_c2l(os.path.join(notebookName, noteName + '.md'))):
            fileDir = self.__str_c2l(os.path.join(notebookName, noteName + '.md'))
        elif os.path.exists(os.path.join(notebookName, noteName + '.txt')):
            fileDir = self.__str_c2l(os.path.join(notebookName, noteName + '.txt'))
        else:
            return -1
        if self.lastUpdate < note.updated / 1000:
            if self.lastUpdate < os.stat(fileDir).st_mtime:
                return 0
            else:
                return -1
        else:
            if self.lastUpdate < os.stat(fileDir).st_mtime:
                return 1
            else:
                return 2
    def __get_file_content(self, fileDir):
        with open(fileDir) as f:
            c = f.read()
            c = c.decode(chardet.detect(c)['encoding'] or 'utf8')
        return c
    def __str_c2l(self, s):
        return s.decode('utf8').encode(sys.stdin.encoding)
    def __str_l2c(s):
        try:
            return s.decode(sys.stdin.encoding).encode('utf8')
        except:
            return s.decode(chardet.detect(s)['encoding'] or 'utf8').encode('utf8')
