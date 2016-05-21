import re

from markdown import markdown as md
from html2text import html2text as h2t

def markdown(s):
    s = md(s, extensions=['markdown.extensions.fenced_code', 'markdown.extensions.tables'])
    s = re.compile('<code[^>]*?>').sub('<code>', s)
    return s

def html2text(s):
    s = re.compile('</*en-media[^>]*?>').sub('', s)
    return h2t(s)
