#coding=utf8
import sys, os, json, time

from controllers import Controller
from evernoteapi.oauth import Oauth


def sys_print(s, level = 'info'):
    print(('[%-4s] %s'%((level+' '*4)[:4].upper(), s)).encode(sys.stdin.encoding))
def sys_input(s):
    return raw_input(s.encode(sys.stdin.encoding))
def show_help(*args):
    for fn, h in argDict.iteritems():
        print('%-10s: %s'%(fn, h[1].decode('utf8').encode(sys.stdin.encoding)))
def init(*args):
    mainController = Controller()
    def clear_dir():
        if sys_input(u'初始化目录将会清除目录下所有文件，是否继续？[yn]') != 'y': return False
        def _clear_dir(currentDir):
            dirs, files = os.walk(currentDir).next()[1:]
            for d in dirs:
                _clear_dir(os.path.join(currentDir, d))
                os.rmdir(os.path.join(currentDir, d))
            for f in files: os.remove(os.path.join(currentDir, f))
        _clear_dir('.')
        return True
    def _init(*args):
        if not reduce(lambda x,y: x+y, [l for l in os.walk('.').next()[1:]]) or clear_dir():
            sys_print(u'账户仅需要在第一次使用时设置一次')
            while 1:
                sandbox = sys_input(u'是否是沙盒环境？[yn]') == 'y'
                isInternational = False
                expireTime = None
                isSpecialToken = sys_input(u'是否使用开发者Token？[yn]') == 'y'
                if isSpecialToken:
                    token = sys_input(u'开发者Token: ')
                else:
                    sys_print(u'本地删除笔记本将不会同步到云端，但笔记会照常删除')
                    if not sandbox: isInternational = sys_input(u'是否是国际用户？[yn]') == 'y'
                    token, expireTime = Oauth(sandbox = sandbox, isInternational = isInternational).oauth()
                if token:
                    mainController.log_in(token=token, isSpecialToken=isSpecialToken, sandbox=sandbox,
                            isInternational = isInternational, expireTime = expireTime / 1000)
                    if mainController.available:
                        mainController.ls.update_config(token=token, isSpecialToken=isSpecialToken,
                                sandbox=sandbox, isInternational=isInternational,
                                expireTime=expireTime / 1000)
                        sys_print(u'登陆成功')
                        break
                    else:
                        sys_print(u'登录失败')
                        if sys_input(u'重试登录？[yn]') != 'y': break
                else:
                    sys_print(u'登录失败')
                    if sys_input(u'重试登录？[yn]') != 'y': break
    if mainController.available:
        if sys_input(u'已经登录，是否要重新登录？[yn]') == 'y': _init(*args)
    else:
        _init(*args)
    print('Bye~')
def config(*args):
    mainController = Controller()
    if mainController.available:
        sys_print(u'目前登录用户： ' + mainController.ec.userStore.getUser().username)
    else:
        sys_print(u'尚未登录', 'warn')
def pull(*args):
    mainController = Controller()
    if mainController.available:
        mainController.fetch_notes()
        # show changes
        for change in mainController.get_changes():
            if change[1] in (-1, 0): sys_print(change[0].decode('utf8'), 'down')
        # confirm
        if sys_input(u'是否更新本地文件？[yn]') == 'y':
            mainController.download_notes(False)
        print('Bye~')
    else:
        sys_print(u'尚未登录', 'warn')
def push(*args):
    mainController = Controller()
    if mainController.available:
        mainController.fetch_notes()
        # show changes
        for change in mainController.get_changes():
            if change[1] in (1, 0): sys_print(change[0].decode('utf8'), 'down')
        # confirm
        if sys_input(u'是否上传本地文件？[yn]') == 'y':
            mainController.upload_files(False)
        print('Bye~')
    else:
        sys_print(u'尚未登录', 'warn')
def status(*args):
    mainController = Controller()
    if mainController.available:
        mainController.fetch_notes()
        # show changes
        for change in mainController.get_changes():
            if change[1] == -1:
                sys_print(change[0].decode('utf8'), 'down')
            elif change[1] == 1:
                sys_print(change[0].decode('utf8'), 'uplo')
            elif change[1] == 0:
                sys_print(change[0].decode('utf8'), 'both')
    else:
        sys_print(u'尚未登录', 'warn')

argDict = {
    'help': (show_help, '显示帮助'),
    'init': (init, '登陆localnote'),
    'config': (config, '查看已经登录的账户'),
    'pull': (pull, '下载云端笔记'),
    'push': (push, '上传本地笔记'),
    'status': (status, '查看本地及云端更改'),
}

def main():
    del sys.argv[0]
    if not sys.argv: sys.argv.append('help')
    argDict.get(sys.argv[0], (show_help,))[0](sys.argv[1:])

if __name__ == '__main__':
    main()
