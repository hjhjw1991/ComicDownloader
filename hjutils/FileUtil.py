# -*- coding:utf-8 -*-
import os
import chardet


def encode(encoding):
    def wrapper(func):
        def method(*args, **kvargs):
            (dirs, files) = func(*args, **kvargs)
            newdirs = []
            newfiles = []
            if dirs:
                for d in dirs:
                    newdirs.append(d.decode(chardet.detect(d).get('encoding', 'utf-8')).encode(encoding))
            if files:
                for f in files:
                    newfiles.append(f.decode(chardet.detect(f).get('encoding', 'utf-8')).encode(encoding))
            return (newdirs, newfiles)
        return method
    return wrapper


@encode('utf-8')
def getDirsAndFiles(dir, ext=""):
    """
    在指定目录下获取全部直接子目录和文件的路径, 
    @dir 指定目录, 
    @ext 指定文件扩展名,默认匹配所有扩展名, 
    @return 返回一个二元tuple,第一个是目录list,第二个是文件list.
    """
    if not (os.path.exists(dir) or os.path.isdir(dir)):
      return
    files = []
    dirs = []
    for file in os.listdir(dir):
        abspath = '/'.join([dir,file])
        if os.path.isdir(abspath):
          dirs.append(abspath)
        elif ext=="" or abspath[-len(ext):]==ext:
          files.append(abspath)
    return (dirs,files)


def getFilesRecursively(dir, extension=""):
    """
    获取指定目录下所有文件的路径,调用 getDirsAndFiles 方法实现,
    @dir 目录,
    @extension 文件后缀,
    @return 返回文件路径list.
    """
    (dirs,files) = getDirsAndFiles(dir, extension)
    ret = files
    while dirs:
        newdirs = []
        for dir in dirs:
            (ddir,files) = getDirsAndFiles(dir, ext=extension)
            newdirs.extend(ddir)
            ret.extend(files)
        dirs = newdirs
    return ret


def getAbsolutePath(path):
    return os.path.abspath(path)


def ensurePath(dir):
    if not dir:
        raise ValueError("path is None")
    path = os.path.abspath(dir)
    if os.path.exists(path):
        return True
    return os.makedirs(path)


def testGetDirsAndFiles():
    print(getDirsAndFiles(os.path.abspath("..")))


if __name__=="__main__":
    testGetDirsAndFiles()
