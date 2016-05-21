#coding=utf8
import sys, os, json, time

from controllers import Controller, convert_html
from evernoteapi.oauth2 import Oauth


def sys_print(s, level = 'info'):
    print(('[%-4s] %s'%((level+' '*4)[:4].upper(), s)).encode(sys.stdin.encoding))
def sys_input(s):
    return raw_input(s.encode(sys.stdin.encoding))
def check_files_format(fn):
    def _check_files_format(*args, **kwargs):
        mainController = Controller()
        configFound, wrongFiles = mainController.check_files_format()
        if not configFound:
            sys_print(u'检测到你不在印象笔记主目录中，或配置文件损坏', 'warn')
        elif mainController.available:
            if wrongFiles:
                for fileName, status in wrongFiles:
                    if status == 1:
                        sys_print(u'检测到错误放置的内容：'+fileName.decode('utf8'), 'warn')
                    elif status == 2:
                        sys_print(u'检测到内容过大的文件：'+fileName.decode('utf8'), 'warn')
                    elif status == 3:
                        sys_print(u'检测到意义不明的文件：'+fileName.decode('utf8'), 'warn')
                sys_print(u'请确保单条笔记有md或html的正文且不大于%s字节，笔记中没有文件夹格式的附件。'%mainController.ls.maxUpload, 'info')
            else:
                return fn(mainController, *args, **kwargs)
        else:
            sys_print(u'尚未登录', 'warn')
    return _check_files_format
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
                    if not sandbox: isInternational = sys_input(u'是否是国际用户？[yn]') == 'y'
                    token, expireTime = Oauth(sandbox = sandbox, isInternational = isInternational).oauth()
                    # Use special oauth to get token
                    isSpecialToken = True
                if token:
                    mainController.log_in(token=token, isSpecialToken=isSpecialToken, sandbox=sandbox,
                            isInternational = isInternational, expireTime = expireTime)
                    if mainController.available:
                        mainController.ls.update_config(token=token, isSpecialToken=isSpecialToken,
                                sandbox=sandbox, isInternational=isInternational,
                                expireTime = expireTime)
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
@check_files_format
def config(mainController, *args):
    sys_print(u'目前登录用户： ' + mainController.ec.userStore.getUser().username)
@check_files_format
def pull(mainController, *args):
    mainController.fetch_notes()
    # show changes
    for change in mainController.get_changes():
        if change[1] in (-1, 0, 1): sys_print(change[0].decode('utf8'), 'pull')
    # confirm
    if sys_input(u'是否更新本地文件？[yn]') == 'y':
        mainController.download_notes(False)
    print('Bye~')
@check_files_format
def push(mainController, *args):
    mainController.fetch_notes()
    # show changes
    for change in mainController.get_changes():
        if change[1] in (1, 0): sys_print(change[0].decode('utf8'), 'push')
    # confirm
    if sys_input(u'是否上传本地文件？[yn]') == 'y':
        mainController.upload_files(False)
    print('Bye~')
@check_files_format
def status(mainController, *args):
    mainController.fetch_notes()
    # show changes
    changes = mainController.get_changes()
    if changes:
        for change in changes:
            if change[1] == -1:
                sys_print(change[0].decode('utf8'), 'pull')
            elif change[1] == 1:
                sys_print(change[0].decode('utf8'), 'push')
            elif change[1] == 0:
                sys_print(change[0].decode('utf8'), 'both')
    else:
        sys_print(u'云端和本地笔记都处于已同步的最新状态。')
def convert(*args):
    if 0 < len(args):
        fileName, ext = os.path.splitext(args[0])
        if sys_input(u'将会生成：%s，是否继续？[yn] '%(fileName.decode(sys.stdin.encoding) + '.md')) != 'y': return
        status = convert_html(args[0])
        if status in (1, 2, 4):
            if status == 1:
                sys_print(u'仅能转换html文件', 'warn')
            elif status == 2:
                sys_print(u'没有找到此文件', 'warn')
            else:
                sys_print(u'无法正常解码，请尝试Utf8编码')
            return
        else:
            if status == 3:
                if sys_input(u'已检测到同名.md文件，是否继续写入？[yn] ') != 'y':
                    return
                else:
                    status = convert_html(args[0], 
                            sys_input(u'是否覆盖写入，否将自动添加后缀[yn]') == 'y')
            sys_print(u'已成功生成%s。'%status.decode(sys.stdin.encoding))
    else:
        sys_print(u'使用方式：localnote convert 需要转换的文件.html')

argDict = {
    'help': (show_help, '显示帮助'),
    'init': (init, '登陆localnote'),
    'config': (config, '查看已经登录的账户'),
    'pull': (pull, '下载云端笔记'),
    'push': (push, '上传本地笔记'),
    'status': (status, '查看本地及云端更改'),
    'convert': (convert, '将html文件转为markdown格式')
}

def main():
    del sys.argv[0]
    if not sys.argv: sys.argv.append('help')
    argDict.get(sys.argv[0], (show_help,))[0](*sys.argv[1:])

if __name__ == '__main__':
    main()
