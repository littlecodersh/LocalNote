# LocalNote

[![Gitter](https://badges.gitter.im/littlecodersh/LocalNote.svg)](https://gitter.im/littlecodersh/LocalNote?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge) ![python](https://img.shields.io/badge/python-2.7-ff69b4.svg) [中文版](https://github.com/littlecodersh/LocalNote/blob/master/README.md)

LocalNote enables you to use evernote in the local-file way.

Popular markdown format is supported and can be perfectly performed in evernote (the download format will remain as .md instead of .html).

Majority of notes in evernote can also be translated into markdown format easily.

LocalNote is also available on three platforms, which ensure that linux users can also have a good experience with evernote.

# Screenshot

![](http://7xrip4.com1.z0.glb.clouddn.com/LocalNote/localnote.gif)

Video is [here](http://v.youku.com/v_show/id_XMTU3Nzc5NzU1Ng==)

# Installation

```bash
pip install localnote
```

# Usage

## Commonly used commands

```bash
# initialize the root folder, please use this in an empty folder
localnote init
# download your notes from your evernote to your computer
localnote pull
# show the difference between your local notes and online notes
localnote status
# upload your notes from your computer to your evernote
localnote push
# translate html documents into markdown formats
localnote convert File_Need_Convert.html
```

## Patterns

You may use your whole evernote with LocalNote, or choose the ones you like.

```bash
# Set notebooks that sync with LocalNote
localnote notebook
```
## Storage format
* A folder in the root folder means a notebook
* A document, folder as well, in notebook folder means a note
* A note can contain main document only or have attachments in any format.
* Main document of a note must be a `.md` or `.html` file, its file name will be used as note name.

## Example file tree

```
Root
    My default notebook 
        My first notebook.html
        My second notebook.html
    Attachment notebook
        My third notebook
            My third notebook.md
            Packed documents.zip
            Note of packing.txt
    Empty notebook
```

# FAQ

Q: Will the first pull take a long time?

A: It depands how big your files are, the downloading speed is about 200k/s.

Q: How to preview markdown files locally?

A: You need a web browser plugin. Take Chrom for example, it's [Markdown Preview Plus](https://chrome.google.com/webstore/detail/markdown-preview-plus/febilkbfcbhebfnokafefeacimjdckgl)。

# Comments

If you have any question or suggestion, you can discuss with me in this [Issue](https://github.com/littlecodersh/LocalNote/issues/1).

Or you may contact me on gitter: [![Gitter](https://badges.gitter.im/littlecodersh/LocalNote.svg)](https://gitter.im/littlecodersh/LocalNote?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
