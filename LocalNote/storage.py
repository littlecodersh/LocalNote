import json, os, time
from markdown2 import markdown

from evernoteapi import EvernoteController

CONFIG_DIR = 'user.cfg'

class Storage(object):
    def __init__(self):
        self.token, self.isSpecialToken, self.sandbox, self.isInternational, self.expireTime, self.lastUpdate = self.__load_config()
        self.available, self.ec = self.__check_available()
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
        for nbName, notebook in self.ec.storage.storage.iteritems():
            if not os.path.exists(nbName): os.mkdir(nbName)
            for nName, note in notebook.get('notes', {}).iteritems():
                if not self.__check_file(nName, nbName, note) in (-1, 0): continue
                attachmentDict = self.ec.get_attachment('%s/%s'%(nbName, nName))
                if '%s.md'%nName in attachmentDict.keys():
                    with open(os.path.join(nbName, '%s.md'%nName), 'wb') as f: f.write(attachmentDict['%s.md'%nName])
                else:
                    with open(os.path.join(nbName, '%s.txt'%nName), 'w') as f: f.write(self.ec.get_content('%s/%s'%(nbName, nName)))
        self.lastUpdate = time.time()
        return True
    def get_changes(self):
        r = ''
        if not self.available: return r
        for nbName, notebook in self.ec.storage.storage.iteritems():
            if not os.path.exists(nbName):
                r += 'deleted %s/'%nbName
            else:
                for nName, note in notebook.get('notes', {}).iteritems():
                    if not any(os.path.exists(os.path.join(nbName, nName + postfix)) for postfix in ('.md', '.txt')):
                        r += 'deleted %s/%s'%(nbName, nName)
                    elif self.__check_file(nName, nbName, note) in (1, 0):
                        r += 'changed %s/%s'%(nbName, nName)
        return r
    def upload_file(self):
        if not self.available: return False
        for nbName, notebook in self.ec.storage.storage.iteritems():
            if not os.path.exists(nbName):
                self.ec.delete_notebook(nbName)
            else:
                for nName, note in notebook.get('notes', {}).iteritems():
                    if not any(os.path.exists(os.path.join(nbName, nName + postfix)) for postfix in ('.md', '.txt')):
                        self.ec.delete_note('%s/%s'%(nbName, nName))
                    elif self.__check_file(nName, nbName, note) in (1, 0):
                        if os.path.exists(os.path.join(nbName, nName + '.md')):
                            with open(os.path.join(nbName, nName + '.md')) as f:
                                self.ec.update_note('%s/%s'%(nbName, nName), markdown(f.read()), os.path.join(nbName, nName + '.md'))
                        elif os.path.exists(os.path.join(nbName, nName + '.txt')):
                            with open(os.path.join(nbName, nName + '.txt')) as f:
                                self.ec.update_note('%s/%s'%(nbName, nName), f.read())
        return True
    def __check_file(self, noteName, notebookName, note):
        # -1 for need download, 1 for need upload, 0 for can be uploaded and downloaded, 2 for updated
        if os.path.exists(os.path.join(notebookName, noteName + '.md')):
            fileDir = os.path.join(notebookName, noteName + '.md')
        elif os.path.exists(os.path.join(notebookName, noteName + '.txt')):
            fileDir = os.path.join(notebookName, noteName + '.txt')
        else:
            return -1
        if self.lastUpdate < note.updated:
            if self.lastUpdate < os.stat(fileDir).st_ctime:
                return 0
            else:
                return -1
        else:
            if self.lastUpdate < os.stat(fileDir).st_ctime:
                return 1
            else:
                return 2
