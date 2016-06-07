import json, os, time, sys, re
from os.path import join, exists
import chardet

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
    def __init__(self, maxUpload = 0):
        self.maxUpload = maxUpload
        self.token, self.isSpecialToken, self.sandbox, self.isInternational, self.expireTime, self.lastUpdate, self.notebooks = self.__load_config()
        self.encoding = sys.stdin.encoding
    def __load_config(self):
        if not exists(CONFIG_DIR): return '', False, True, False, 0, 0, None
        with open(CONFIG_DIR) as f: r = json.loads(f.read())
        notebooks = r.get('notebooks')
        if notebooks is not None: notebooks = [nb.encode('utf8') for nb in notebooks]
        return (r.get('token', ''), r.get('is-special-token', False), r.get('sandbox', True),
                r.get('is-international', False), r.get('expire-time', 0), r.get('last-update', 0), notebooks)
    def __store_config(self):
        with open(CONFIG_DIR, 'w') as f:
            notebooks = self.notebooks
            if notebooks is not None: notebooks = [nb.decode('utf8') for nb in notebooks]
            f.write(json.dumps({
                'token': self.token,
                'is-special-token': self.isSpecialToken,
                'sandbox': self.sandbox,
                'is-international': self.isInternational,
                'expire-time': self.expireTime,
                'last-update': self.lastUpdate,
                'notebooks': notebooks }))
    def update_config(self, token=None, isSpecialToken=None, sandbox=None, isInternational=None, expireTime=None, lastUpdate=None, notebooks = None):
        if not token is None: self.token = token
        if not isSpecialToken is None: self.isSpecialToken = isSpecialToken
        if not sandbox is None: self.sandbox = sandbox
        if not isInternational is None: self.isInternational = isInternational
        if not expireTime is None: self.expireTime = expireTime
        if not lastUpdate is None: self.lastUpdate = lastUpdate
        if not notebooks is None: self.notebooks = notebooks
        self.__store_config()
    def get_config(self):
        return self.token, self.isSpecialToken, self.sandbox, self.isInternational, self.expireTime, self.lastUpdate, self.notebooks
    def __str_c2l(self, s):
        return s.decode('utf8').encode(sys.stdin.encoding)
    def __str_l2c(self, s):
        try:
            return s.decode(sys.stdin.encoding).encode('utf8')
        except:
            return s.decode(chardet.detect(s)['encoding'] or 'utf8').encode('utf8')
    def read_note(self, noteFullPath):
        attachmentDict = {}
        if exists(self.__str_c2l(join(*noteFullPath))): # note is a foldernote
            for attachment in os.walk(self.__str_c2l(join(*noteFullPath))).next()[2]:
                with open(self.__str_c2l(join(*(noteFullPath))) + os.path.sep + attachment, 'rb') as f:
                    attachmentDict[self.__str_l2c(attachment)] = f.read()
        else: # note is a pure file
            fileList = os.walk(self.__str_c2l(join(*noteFullPath[:-1]))).next()[2]
            for postfix in ('.md', '.html'):
                fName = noteFullPath[-1] + postfix
                if self.__str_c2l(fName) in fileList:
                    with open(self.__str_c2l(join(*noteFullPath)) + postfix, 'rb') as f:
                        attachmentDict[fName] = f.read()
        return attachmentDict
    def write_note(self, noteFullPath, contentDict = {}):
        if 1 < len(noteFullPath):
            nbName, nName = [self.__str_c2l(s) for s in noteFullPath]
            # clear environment
            if exists(nbName):
                for postfix in ('.md', '.html'):
                    if exists(join(nbName, nName+postfix)): os.remove(join(nbName, nName+postfix))
                if exists(join(nbName, nName)):
                    clear_dir(join(nbName, nName))
                    os.rmdir(join(nbName, nName))
            else:
                os.mkdir(nbName)
            # download files
            if not contentDict:
                pass
            elif len(contentDict) == 1:
                for k, v in contentDict.items():
                    self.write_file(noteFullPath, v, os.path.splitext(k)[1])
            else:
                if not exists(join(nbName, nName)): os.mkdir(join(nbName, nName))
                for k, v in contentDict.iteritems():
                    self.write_file(noteFullPath+[k], v, '') # ok, this looks strange, ext is included in k
        else:
            if contentDict: # create folder
                if not exists(self.__str_c2l(noteFullPath[0])): os.mkdir(self.__str_c2l(noteFullPath[0]))
            else: # delete folder
                noteFullPath = self.__str_c2l(noteFullPath[0])
                if exists(noteFullPath):
                    clear_dir(noteFullPath)
                    os.rmdir(noteFullPath)
    def write_file(self, noteFullPath, content, postfix = '.md'):
        if len(noteFullPath) < 1: return False
        if not exists(self.__str_c2l(noteFullPath[0])):
            os.mkdir(self.__str_c2l(noteFullPath[0]))
        try:
            noteFullPath[1] += postfix
            with open(self.__str_c2l(join(*noteFullPath)), 'wb') as f: f.write(content)
            return True
        except:
            return False
    def get_file_dict(self, notebooksList = None):
        fileDict = {}
        for nbName in os.walk('.').next()[1]: # get folders
            nbNameUtf8 = self.__str_l2c(nbName)
            if notebooksList is not None and nbNameUtf8 not in notebooksList: continue
            if nbNameUtf8 == '.DS_Store': continue # Mac .DS_Store ignorance
            fileDict[nbNameUtf8] = []
            for nName in reduce(lambda x,y: x+y, os.walk(nbName).next()[1:]): # get folders and files
                if nName == '.DS_Store': continue # Mac .DS_Store ignorance
                filePath = join(nbName, nName)
                if os.path.isdir(filePath):
                    fileDict[nbNameUtf8].append((self.__str_l2c(nName), os.stat(filePath).st_mtime))
                else:
                    fileDict[nbNameUtf8].append((self.__str_l2c(os.path.splitext(nName)[0]), os.stat(filePath).st_mtime))
        return fileDict
    def check_files_format(self):
        try:
            with open('user.cfg') as f: j = json.loads(f.read())
            if len(j) != 7: raise Exception
            for k in j.keys():
                if k not in ('token', 'is-special-token', 'sandbox', 'notebooks',
                        'is-international', 'expire-time', 'last-update'):
                    raise Exception
        except:
            return False, []
        r = [] # (filename, status) 1 for wrong placement, 2 for too large, 3 for missing main file
        notebooks, notes = os.walk('.').next()[1:]
        for note in notes:
            if note not in ('user.cfg', '.DS_Store'): r.append((self.__str_l2c(note), 1))
        for notebook in notebooks:
            if notebook == '.DS_Store': # Mac .DS_Store ignorance
                r.append(('.DS_Store', 1))
                continue
            folderNotes, notes = os.walk(notebook).next()[1:]
            for note in notes:
                if note == '.DS_Store': continue# Mac .DS_Store ignorance
                if re.compile('.+\.(md|html)').match(note):
                    if self.maxUpload < os.path.getsize(join(notebook, note)):
                        r.append((self.__str_l2c(join(notebook, note)), 2))
                else:
                    r.append((self.__str_l2c(join(notebook, note)), 3))
            for folderNote in folderNotes:
                if folderNote == '.DS_Store':
                    r.append((self.__str_l2c(join(notebook, folderNote)), 1))
                    continue# Mac .DS_Store ignorance
                size = 0
                wrongFolders, attas = os.walk(join(notebook, folderNote)).next()[1:]
                if filter(lambda x: re.compile('.+\.(md|html)').match(x), attas) == []:
                    r.append((self.__str_l2c(join(notebook, folderNote)), 3))
                for atta in attas: size += os.path.getsize(join(notebook, folderNote, atta))
                for wrongFolder in wrongFolders:
                    r.append((self.__str_l2c(join(notebook, folderNote, wrongFolder)), 1))
                if self.maxUpload < size:
                    r.append((self.__str_l2c(join(notebook, folderNote)), 2))
        return True, r

def clear_dir(currentDir):
    dirs, files = os.walk(currentDir).next()[1:]
    for d in dirs:
        clear_dir(os.path.join(currentDir, d))
        os.rmdir(os.path.join(currentDir, d))
    for f in files: os.remove(os.path.join(currentDir, f))
