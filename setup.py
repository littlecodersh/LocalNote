#coding=utf8
""" A command line tool to use evernote locally
See:
https://github.com/littlecodersh/LocalNote
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='LocalNote',

    version='1.0.1',

    description='LocalNote让你能够像使用本地文件一样使用印象笔记，支持markdown语法。Use your evernote like local file system in all platforms (markdown supported)',

    long_description=long_description,

    url='https://github.com/littlecodersh/LocalNote',

    author='LittleCoder',
    author_email='i7meavnktqegm1b@qq.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2.7',
    ],

    keywords='evernote local markdown python',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(),

    install_requires=['requests', 'markdown', 'evernote'],

    # List additional groups of dependencies here
    extras_require={},
    entry_points={
        'console_scripts':[
            'localnote = LocalNote.main:main'
        ]
    },
)
