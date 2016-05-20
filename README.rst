LocalNote |Gitter| |Python27|
=============================

LocalNote让你能够像使用本地文件一样使用印象笔记。

支持流行的markdown格式的笔记，印象笔记中完美显示，上传重新下载笔记仍可编辑。

三平台支持，在linux平台也流畅的使用印象笔记。

欢迎在 `Github <https://github.com/littlecodersh/LocalNote>`__ 参与项目，提交反馈。

**Screenshot**

|GifDemo|

视频见 `这里 <http://v.youku.com/v_show/id_XMTU3Nzc5NzU1Ng==>`__

**Installation**

.. code:: bash

    pip install localnote

**Usage**

常用命令

.. code:: bash

    # 初始化印象笔记目录，请在空文件夹使用
    localnote init
    # 下载笔记
    localnote pull
    # 查看云端及本地笔记更改
    localnote status
    # 上传本地笔记
    localnote push

存储格式

- 根目录下每个文件夹对应一个笔记本
- 笔记本文件夹中每个文件（文件夹）对应一个笔记
- 笔记可以仅存在主文件也可以以文件夹的形式包含附件
- 笔记主文件必须是`.md`或者`.html`格式，文件名（不包括后缀）将会被用作笔记名

示例文件树

::

    Root
        我的默认笔记本
            第一个笔记.html
            第二个笔记.html
        附件笔记本
            第三个笔记
                第三个笔记.md
                打包材料.zip
                打包笔记.txt
        空笔记本

**Comments**

如果有什么问题或者建议都可以在这个 `Issue <https://github.com/littlecodersh/LocalNote/issues/1>`__ 和我讨论。

或者也可以在gitter上交流： |Gitter|

.. |Python27| image:: https://img.shields.io/badge/python-2.7-ff69b4.svg
.. |Gitter| image:: https://badges.gitter.im/littlecodersh/LocalNote.svg
    :target: https://github.com/littlecodersh/ItChat/tree/robot
.. |GifDemo| image:: http://7xrip4.com1.z0.glb.clouddn.com/LocalNoteDemo.gif
