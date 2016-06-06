#coding=utf8
import sys, hashlib, re, time, mimetypes

import evernote.edam.type.ttypes as Types
import evernote.edam.notestore.NoteStore as NoteStore
from evernote.edam.error.ttypes import EDAMUserException
from evernote.api.client import EvernoteClient

from storage import Storage

class EvernoteController(object):
    def __init__(self, token, isSpecialToken = False, sandbox = False, isInternational = False, notebooks = None):
        self.token = token
        if sandbox:
            self.client = EvernoteClient(token=self.token)
        elif isInternational:
            self.client = EvernoteClient(token=self.token, service_host='www.evernote.com')
        else:
            self.client = EvernoteClient(token=self.token, service_host='app.yinxiang.com')
        self.isSpecialToken = isSpecialToken
        self.userStore = self.client.get_user_store()
        self.noteStore = self.client.get_note_store()
        self.storage = Storage(notebooks)
    def get_upload_limit(self):
        return {
            1: 25 * 1024 * 1024,
            3: 100 * 1024 * 1024,
            5: 200 * 1024 * 1024,
        }.get(self.userStore.getUser().privilege, 0)
    def create_notebook(self, noteFullPath):
        if self.get(noteFullPath): return False
        notebook = Types.Notebook()
        notebook.name = noteFullPath
        try:
            notebook = self.noteStore.createNotebook(notebook)
        except EDAMUserException, e:
            if e.errorCode == 10 and e.parameter == 'Notebook.name':
                self.storage.update(self.token, self.noteStore)
                return True
            else:
                raise e
        self.storage.create_notebook(notebook)
        return True
    def create_note(self, noteFullPath, content = '', fileDict = {}):
        if self.get(noteFullPath): return False
        if 1 < len(noteFullPath):
            notebook = noteFullPath[0]
            title = noteFullPath[1]
        else:
            notebook = self.storage.defaultNotebook
            title = noteFullPath[0]
        note = Types.Note()
        note.title = title
        note.content = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
        note.content += '<en-note>'
        content = re.sub('<en-media.*?/>', '', content)
        note.content += content
        if self.get([notebook]) is None: self.create_notebook(notebook)
        note.notebookGuid = self.get([notebook]).guid
        if fileDict:
            note.resources = []
            for fileName, fileBytes in fileDict.iteritems():
                fileData = Types.Data()
                fileData.bodyHash = self._md5(fileBytes)
                fileData.size = len(fileBytes)
                fileData.body = fileBytes
                fileAttr = Types.ResourceAttributes()
                fileAttr.fileName = fileName
                fileAttr.attachment = True
                fileResource = Types.Resource()
                fileResource.data = fileData
                fileResource.mime = mimetypes.guess_type(fileName)[0] or 'application/octet-stream'
                fileResource.attributes = fileAttr
                note.resources.append(fileResource)
                note.content += '<en-media type="%s" hash="%s"/>'%(fileResource.mime, fileData.bodyHash)
        note.content += '</en-note>'
        note = self.noteStore.createNote(note)
        self.storage.create_note(note, notebook)
        return True
    def update_note(self, noteFullPath, content = None, fileDict = {}):
        note = self.get(noteFullPath)
        if note is None: return self.create_note(noteFullPath, content or '', fileDict)
        if 1 < len(noteFullPath):
            notebook = noteFullPath[0]
            title = noteFullPath[1]
        else:
            notebook = self.storage.defaultNotebook
            title = noteFullPath[0]
        oldContent = self.get_content(noteFullPath)
        content = content or oldContent
        header = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
        guid = note.guid
        content = re.sub('<en-media.*?/>', '', content)
        note = Types.Note()
        note.guid = guid
        note.title = title
        note.content = header
        note.content += '<en-note>'
        note.content += content
        if fileDict:
            note.resources = []
            for fileName, fileBytes in fileDict.iteritems():
                fileData = Types.Data()
                fileData.bodyHash = self._md5(fileBytes)
                fileData.size = len(fileBytes)
                fileData.body = fileBytes
                fileAttr = Types.ResourceAttributes()
                fileAttr.fileName = fileName
                fileAttr.attachment = True
                fileResource = Types.Resource()
                fileResource.data = fileData
                fileResource.mime = mimetypes.guess_type(fileName)[0] or 'application/octet-stream'
                fileResource.attributes = fileAttr
                note.resources.append(fileResource)
                note.content += '<en-media type="%s" hash="%s"/>'%(fileResource.mime, fileData.bodyHash)
        note.content += '</en-note>'
        self.noteStore.updateNote(self.token, note)
        self.storage.delete_note(noteFullPath)
        self.storage.create_note(note, notebook)
        return True
    def get_content(self, noteFullPath):
        note = self.get(noteFullPath)
        if note is None: return
        r = self.noteStore.getNoteContent(note.guid)
        try:
            content = re.compile('[\s\S]*?<en-note[^>]*?>([\s\S]*?)</en-note>').findall(r)[0]
        except:
            content = ''
        return content
    def get_attachment(self, noteFullPath):
        note = self.get(noteFullPath)
        attachmentDict = {}
        for resource in (self.noteStore.getNote(note.guid, False, True, False, False).resources or {}):
            attachmentDict[resource.attributes.fileName] = resource.data.body
        return attachmentDict
    def move_note(self, noteFullPath, _to):
        if self.get(noteFullPath) is None: return False
        if len(noteFullPath) < 2 or 1 < len(_to): raise Exception('Type Error')
        self.noteStore.copyNote(self.token, self.get(noteFullPath).guid, self.get(_to).guid)
        if self.isSpecialToken:
            self.noteStore.expungeNote(self.token, self.get(noteFullPath).guid)
        else:
            self.noteStore.deleteNote(self.token, self.get(noteFullPath).guid)
        self.storage.move_note(noteFullPath, _to)
        return True
    def delete_note(self, noteFullPath):
        note = self.get(noteFullPath)
        if note is None: return False
        if len(noteFullPath) < 2: raise Exception('Types Error')
        self.noteStore.deleteNote(self.token, note.guid)
        self.storage.delete_note(noteFullPath)
        return True
    def delete_notebook(self, noteFullPath):
        if not self.get(noteFullPath) or not self.isSpecialToken: return False
        if 1 < len(noteFullPath): raise Exception('Types Error')
        self.noteStore.expungeNotebook(self.token, self.get(noteFullPath).guid)
        self.storage.delete_notebook(noteFullPath)
        return True
    def get(self, s):
        return self.storage.get(s)
    def show_notebook(self):
        self.storage.show_notebook()
    def show_notes(self, notebook=None):
        self.storage.show_notes(notebook)
    def _md5(self, s):
        m = hashlib.md5()
        m.update(s)
        return m.hexdigest()

if __name__ == '__main__':
    # You can get this from 'https://%s/api/DeveloperToken.action'%SERVICE_HOST >>
    # In China it's https://app.yinxiang.com/api/DeveloperToken.action <<
    token = 'S=s1:U=91eca:E=15be6680420:C=1548eb6d760:P=1cd:A=en-devtoken:V=2:H=026e6ff5f5d0753eb37146a1b4660cc9'
    e = EvernoteController(token, True, True)
    # e.update_note('Hello', 'Test', 'Changed', 'README.md')
    e.create_note(['Test', '中文'], 'Chinese')
