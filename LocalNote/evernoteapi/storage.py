#coding=utf8
import sys
import evernote.edam.type.ttypes as Types
import evernote.edam.notestore.NoteStore as NoteStore

# Data Structure
# notebookName:{
#     'notebook': notebook
#     'notes': {
#         noteName: note
#         ...
#     }
# }
# noteDictFormat: {
# 'notebookName':[('note1', timeStamp), ..],
# }

class Storage():
    storage = {}
    def __init__(self, notebooks = None):
        self.available = False
        self.notebooks = notebooks
    def update(self, token, noteStore):
        f = NoteStore.NoteFilter()
        s = NoteStore.NotesMetadataResultSpec()
        s.includeTitle = True
        s.includeUpdated = True
        for nb in noteStore.listNotebooks():
            if self.notebooks is not None and nb.name not in self.notebooks: continue
            self.storage[nb.name] = {}
            self.storage[nb.name]['notebook'] = nb
            self.storage[nb.name]['notes'] = {}
            f.notebookGuid = nb.guid
            for ns in noteStore.findNotesMetadata(f, 0, 9999, s).notes:
                self.storage[nb.name]['notes'][ns.title] = ns
        self.defaultNotebook = noteStore.getDefaultNotebook(token).name
    def create_note(self, note, notebookName = None):
        if notebookName is None: notebookName = self.defaultNotebook
        if self.get(notebookName) is None: return False
        self.storage[notebookName]['notes'][note.title] = note
        return True
    def create_notebook(self, notebook):
        if self.get(notebook.name) is not None: return False
        self.storage[notebook.name] = {}
        self.storage[notebook.name]['notebook'] = notebook
        self.storage[notebook.name]['notes'] = {}
        return True
    def copy_note(self, noteFullPath, _to = None):
        if _to is None: _to = self.defaultNotebook
        note = self.get(noteFullPath)
        if len(noteFullPath) < 2 or note is None: return False
        self.storage[_to]['notes'][note.title] = note
        return True
    def move_note(self, noteFullPath, _to = None):
        r = self.copy_note(noteFullPath, _to)
        if r == False: return False
        return self.delete_note(noteFullPath)
    def delete_note(self, noteFullPath):
        if self.get(noteFullPath) is None: return False
        del self.storage[noteFullPath[0]]['notes'][noteFullPath[1]]
        return True
    def delete_notebook(self, noteFullPath):
        if self.get(noteFullPath) is None: return False
        del self.storage[noteFullPath[0]]
        return True
    def get(self, l):
        r = self.storage.get(l[0])
        if r is None: return
        if 1 < len(l): return r['notes'].get(l[1])
        return r.get('notebook')
    def get_note_dict(self):
        noteDict = {}
        for nbName, nb in self.storage.iteritems():
            noteDict[nbName] = []
            for nName, n in nb['notes'].iteritems():
                noteDict[nbName].append((nName, n.updated / 1000))
        return noteDict
    def show_notebook(self):
        for bn, nb in self.storage.items(): print_line(bn)
    def show_notes(self, notebook = None):
        for bn, nb in self.storage.items():
            if not notebook: print_line(bn + ':')
            if not notebook or bn == notebook:
                for nn, ns in nb['notes'].items():
                    print_line(('' if notebook else '    ')+nn)
def print_line(s):
    t = sys.getfilesystemencoding()
    print s.decode('UTF-8').encode(t)
