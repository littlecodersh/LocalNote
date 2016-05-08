import time
from markdown2 import markdown

BODY = u'''\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-export SYSTEM "http://xml.evernote.com/pub/evernote-export2.dtd">
<en-export export-date="20160101T000000Z" application="Evernote/Windows" version="6.x">
<note><title>{title}</title><content>
<![CDATA[<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd"><en-note>{content}</en-note>]]>
</content>
<created>{createDate}</created><updated>{updateDate}</updated>
</note></en-export>'''
class Editor(object):
    def __init__(self, title = None, content = '', createDate = None, updateDate = None):
        self.title = title if title else str(int(time.time()))
        self.content = content 
        self.createDate = createDate if createDate else time.time()
        self.updateDate = updateDate if updateDate else time.time()
    def _get_format_date(self, date):
        return '%s%02d%02dT%02d%02d%02dZ'%time.gmtime(date)[:6]
    def set(self, title = None, content = None, createDate = None, updateDate = None):
        if not title is None: self.title = title
        if not content is None: self.content = content
        if not createDate is None: self.createDate = createDate
        if not updateDate is None: self.updateDate = updateDate
    def get_html(self, md = True):
        return BODY.format(
            title = self.title,
            content = markdown(self.content) if md else self.content,
            createDate = self._get_format_date(self.createDate),
            updateDate = self._get_format_date(self.updateDate))

if __name__ == '__main__':
    content = '# Title'
    with open('m.enex', 'w') as f:
        c = Editor('Demo', content, time.time(), time.time()).get_html()
        f.write(c)
