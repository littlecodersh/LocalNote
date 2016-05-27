import re
from lxml import etree
from StringIO import StringIO

from markdown import markdown as md
from html2text import html2text as h2t

with open('enml2.dtd') as f: dtd = f.read()
dtd = etree.DTD(StringIO(dtd))

def markdown(s):
    s = md(s, extensions=['markdown.extensions.fenced_code', 'markdown.extensions.tables'])
    s = re.compile('<code[^>]*?>').sub('<code>', s)
    if not check_dtd(s): raise Exception('Unknown error about xml format caused by md translation, please email the file to i7meavnktqegm1b@qq.com')
    return s

def html2text(s):
    s = re.compile('</*en-media[^>]*?>').sub('', s)
    return h2t(s)

def check_dtd(s):
    return dtd.validate(etree.XML(s))

print check_dtd('<b><a/></b>')
print check_dtd('<code class="Python"></code>')
