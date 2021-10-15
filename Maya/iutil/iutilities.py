# Date: Wed 28/11/2012
# Author : Qurban Ali (qurban.ali@iceanimations.com),
#          Hussain Parsaiyan (hussain.parsaiyan@iceanimations.com)
#          Talha Ahmed (talha.ahmed@iceanimations.com)

import random
import os
import shutil
import warnings
import re
import stat
import subprocess
import sys
import time
import hashlib
import functools
import cProfile
import tempfile
import itertools
import datetime
import collections
from os.path import curdir, join, abspath, splitunc, splitdrive, sep, pardir
import imghdr
import struct
import csv
import string  # for get_drives
import ctypes
from ctypes import wintypes
from ctypes import windll  # for get_drives

op = os.path


class memoize(object):
    '''Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    '''

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        '''Return the function's docstring.'''
        return self.func.__doc__

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return functools.partial(self.__call__, obj)


def get_directory_size(start_path):
    total_size = 0
    for dirpath, _, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return round((total_size / 1024) / 1024, 1)


def getLatestFile(paths):
    '''given a list of file paths, returns a file path having the
    latest timestamp'''
    latest = paths[0]
    for path in paths[1:]:
        if op.getmtime(path) > op.getmtime(latest):
            latest = path
    return latest


def getUsername():
    return os.environ['USERNAME']


def dictionaryToDetails(_dict, anl='Reason'):
    '''converts a dictinary containing key values as strings to a string
    each key value pair separated by \n and each item (key value) both
    separated by \n\n'''
    result = ''
    for key, value in _dict.items():
        if isinstance(value, list):
            value = '\n'.join(value)
        result += '\n\n'.join(['\n%s: '.join([key, value]) % anl])
    return result


def splitPath(path):
    '''splits a file or folder path and returns as a list
    'D:/path/to/folder/or/file' -> ['D:', 'path', 'to', 'folder', 'or', 'file']
    '''
    components = []
    while True:
        (path, tail) = os.path.split(path)
        if tail == "":
            if path:
                components.append(path)
            components.reverse()
            return components
        components.append(tail)


def getCSVFileData(fileName):
    '''returns list of tupples containing the csv file rows separated by
    comma'''
    with open(fileName, 'rb') as csvfile:
        tuples = list(csv.reader(csvfile, delimiter=','))
    return tuples


def basename(path, depth=3):
    '''returns last 'depth' entries in a file or folder path as a string'''
    return op.join(*splitPath(path)[-depth:])


def dirname(path, depth=3):
    '''removes last 'depth' entries from a file or folder path'''
    return op.normpath(op.join(*splitPath(path)[:-depth]))


def mkdir(path, dirs):
    '''makes directories or folders recursively in a given path'''
    for d in splitPath(dirs):
        path = op.join(path, d)
        try:
            os.mkdir(path)
        except:
            pass


def mkdirr(path, mode=0777):
    '''A Wrapper on os.mkdir recursively ensures the existance of parent
    directories before making the given directory'''

    if os.path.exists(path):
        if not os.path.isdir(path):
            raise ValueError('%s is a non-directory' % path)
    else:
        parent_dir = os.path.dirname(path)
        if parent_dir:
            mkdirr(parent_dir, mode)
        os.mkdir(path)


def fileExists(path, fileName):
    for name in os.listdir(path):
        try:
            if re.search(fileName + '_v\d{3}', name):
                return True
        except:
            pass


def getLastVersion(path, fileName, nxt=False):
    versions = []
    for version in os.listdir(path):
        try:
            versions.append(
                int(re.search('_v\d{3}', version).group().split('v')[-1]))
        except AttributeError:
            pass
    if versions:
        temp = max(versions) + 1 if nxt else max(versions)
        return fileName + '_v' + str(temp).zfill(3)


def get_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1
    return drives


def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def get_image_size(fname):
    '''Determine the image type of fhandle and return its size.
    from draco'''
    with open(fname, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return
        if imghdr.what(fname) == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', head[16:24])
        elif imghdr.what(fname) == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif imghdr.what(fname) in ['jpeg', 'jpg']:
            try:
                fhandle.seek(0)  # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception as ex:  # IGNORE:W0703
                print str(ex)
                return
        else:
            return
        return width, height


def resizeImage(image, size):
    command = r"R:\Pipe_Repo\Users\Qurban\applications\ImageMagick\mogrify.exe"
    command += ' -resize ' + size + ' ' + image
    subprocess.call(command, shell=True)


def addFrameNumber(image, frame, outputImage=None):
    res = get_image_size(image)
    if not res:
        raise RuntimeError('Could not find image resolution: %s' % image)
    if not outputImage:
        outputImage = image
    subprocess.call((
        "R:\\Pipe_Repo\\Users\\Qurban\\applications\\ImageMagick\\convert.exe"
        " %s -draw \"text %s\" %s")
        % (image, str(res[0] / 2) + ',' + str(res[1] / 8) + " '%s'" % frame,
           " " + outputImage),
        shell=True)


def paths_equal(path1, path2):
    return op.normpath(op.normcase(path1)) == op.normpath(op.normcase(path2))


def _abspath_split(path):
    abs = abspath(op.normpath(path))
    prefix, rest = splitunc(abs)
    is_unc = bool(prefix)
    if not is_unc:
        prefix, rest = splitdrive(abs)
    return is_unc, prefix, [x for x in rest.split(sep) if x]


def relpath(path, start=curdir):
    """Return a relative version of a path"""

    if not path:
        raise ValueError("no path specified")

    start_is_unc, start_prefix, start_list = _abspath_split(start)
    path_is_unc, path_prefix, path_list = _abspath_split(path)

    if path_is_unc ^ start_is_unc:
        raise ValueError("Cannot mix UNC and non-UNC paths (%s and %s)" %
                         (path, start))
    if path_prefix.lower() != start_prefix.lower():
        if path_is_unc:
            raise ValueError("path is on UNC root %s, start on UNC root %s" %
                             (path_prefix, start_prefix))
        else:
            raise ValueError("path is on drive %s, start on drive %s" %
                             (path_prefix, start_prefix))
    # Work out how much of the filepath is shared by start and path.
    i = 0
    for e1, e2 in zip(start_list, path_list):
        if e1.lower() != e2.lower():
            break
        i += 1

    rel_list = [pardir] * (len(start_list) - i) + path_list[i:]
    if not rel_list:
        return curdir
    return join(*rel_list)


op.relpath = relpath


def isTempPath(path):
    tempdir = tempfile.gettempdir()
    if op.normpath(path).startswith(tempdir):
        return True
    return False


_GetShortPathNameW = windll.kernel32.GetShortPathNameW
_GetShortPathNameW.argtypes = [
    wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD
]
_GetShortPathNameW.restype = wintypes.DWORD


def getShortPathName(long_name):
    """
    Gets the short path name of a given long path.
    http://stackoverflow.com/a/23598461/200291
    """
    output_buf_size = 0
    while True:
        output_buf = ctypes.create_unicode_buffer(output_buf_size)
        needed = _GetShortPathNameW(long_name, output_buf, output_buf_size)
        if output_buf_size >= needed:
            return output_buf.value
        else:
            output_buf_size = needed


_GetLongPathNameW = windll.kernel32.GetLongPathNameW
_GetLongPathNameW.argtypes = [
    wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD
]
_GetLongPathNameW.restype = wintypes.DWORD


def getLongPathName(long_name):
    """
    Gets the short path name of a given long path.
    http://stackoverflow.com/a/23598461/200291
    """
    output_buf_size = 0
    while True:
        output_buf = ctypes.create_unicode_buffer(output_buf_size)
        needed = _GetLongPathNameW(long_name, output_buf, output_buf_size)
        if output_buf_size >= needed:
            return output_buf.value
        else:
            output_buf_size = needed


def getTemp(mkd=False, suffix="", prefix="tmp", directory=None):
    tmp = getattr(tempfile, "mkdtemp" if mkd else "mkstemp")(
        suffix=suffix, prefix=prefix, dir=directory)
    if mkd:
        return getLongPathName(tmp)
    else:
        tmp = tmp[0], getLongPathName(unicode(tmp[1]))
        os.close(tmp[0])
        return tmp[1]


def mayaFile(path):
    '''
    @return True if the file ends with extensions else False
    '''
    extensions = [".ma", ".mb"]
    try:
        path = path.lower()
    except BaseException as e:
        print "util.mayaFile"
        raise e
    for extension in extensions:
        if path.endswith(extension):
            return True
    return False


def getIndPathComps(path):
    '''
    @return: all the path components in a list seperately
    '''
    comps = []
    split = op.split(path)
    while split[1]:
        comps.insert(0, split[1])
        split = op.split(split[0])
    if split[0]:
        comps.insert(0, op.normpath(split[0]))
    return comps


def getPathComps(path):
    '''
    @returns the directory below path
    '''
    pathComps = []
    pathComps.append(path)
    for path in (op.dirname(path) if path != op.dirname(path) else None
                 for _ in path):
        if path:
            pathComps.append(path)
        else:
            break
    return pathComps


def randomString(
        length=5,
        choice='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
):
    return ''.join([random.choice(choice) for _ in range(length)])


def randomNumber():
    return random.random()


def archive(file_dir, file_name, copy=False, alternatePath=""):
    ''' Move the file file_dir, filename to file_dir, .archive, filename,
    file_name_date_modified '''
    # TODO: determine of to archive component who also have
    if alternatePath:
        if not op.exists(alternatePath):
            raise WindowsError
        else:
            fpath = alternatePath
    else:
        fpath = file_dir

    if not haveWritePermission(fpath):
        warnings.warn('Access denied...')
        return

    if not file_name:
        warnings.warn('No file name specified...')
        return
    if not fpath:
        warnings.warn('No file path specified...')
        return

    try:
        dir_names = os.listdir(file_dir)
    except WindowsError:
        warnings.warn('Incorrect path, use / instead of \\ in the path...')
        return

    if file_name not in dir_names:
        warnings.warn('File doesn\'t exist...')
        return

    archive = op.join(fpath, '.archive')
    if '.archive' not in os.listdir(fpath):
        # make .archive directory in case it doesn't exists
        os.mkdir(archive)

    _dir = os.listdir(archive)

    # name of the directory which contains all the version of the file
    fileArchive = op.join(archive, file_name)

    if file_name not in _dir:
        # if directory specific to the file doesn't exists, create one
        os.mkdir(fileArchive)

    fileToArchive = op.join(file_dir, file_name)

    # date the file was modified.
    date = str(
        datetime.datetime.fromtimestamp(op.getmtime(fileToArchive))).replace(
            ':', '-').replace(' ', '_')

    finalPath = op.join(fileArchive, date)

    if op.exists(finalPath):
        if os.listdir(finalPath):
            try:
                if op.getsize(fileToArchive) == op.getsize(
                        op.join(finalPath, filter(lambda theFile: op.isfile(
                                op.join(finalPath, theFile)),
                                os.listdir(finalPath))[0])):
                    return op.join(finalPath, file_name)  # redundant code
                else:
                    finalPath = getTemp(
                        prefix=date + "_", mkd=True, directory=fileArchive)

            except BaseException as e:
                print e
    else:
        pass

    if not op.exists(finalPath):
        os.mkdir(finalPath)

    if copy:
        shutil.copy2(fileToArchive, finalPath)
    else:
        shutil.move(fileToArchive, finalPath)

    return op.join(finalPath, file_name)


def listdir(path, dirs=True):

    path = path if op.isdir(path) else op.dirname(path)
    return filter(
        lambda sibling: not (op.isdir(op.join(path, sibling)) ^ dirs),
        os.listdir(path))


def localPath(path, localDrives):
    try:
        return any((path.lower().find(local_drive) != -1
                    for local_drive in localDrives))
    except BaseException as e:
        print "localPath"
        raise e


def normpath(path):
    return op.abspath(op.normpath(str(path)))


def lowestConsecutiveUniqueFN(dirpath, bname, hasext=True, key=op.exists):
    ext = ""
    if hasext:
        bname, ext = tuple(op.splitext(bname))
    else:
        pass

    # make unique name
    if not key(op.join(dirpath, bname) + ext):
        bname += ext

    else:
        num = 1
        while (True):
            if key(op.join(dirpath, bname + "_" + str(num)) + ext):
                num += 1
                continue
            else:

                bname = bname + "_" + str(num) + ext
                break

    return bname


lCUFN = lowestConsecutiveUniqueFN


def ftn_similarity(ftn1, ftn2, ftn_to_texs):
    texs1 = set(ftn_to_texs[ftn1])
    texs2 = set(ftn_to_texs[ftn2])
    return texs1.intersection(texs2)


def find_related_ftns(myftn, ftn_to_texs):
    '''
    :type ftn: str
    :type ftn_to_texs: dict
    '''
    related_ftns = [myftn]

    similars = []
    for ftn in ftn_to_texs:
        if ftn != myftn and ftn_similarity(myftn, ftn, ftn_to_texs):
            similars.append(ftn)

    related_ftns.extend(similars)
    mytexs = set(ftn_to_texs.pop(myftn))

    for sftn in similars:
        texs, ftns = find_related_ftns(sftn, ftn_to_texs)
        mytexs.update(texs)
        related_ftns.extend(ftns)

    return related_ftns, mytexs


fn_pattern = (
        r'(?P<bn>.*?)(?P<sep>[._])?'
        r'(?P<tok>-?\d+|u\d_v\d|\<udim\>|u\<U\>_v\<V\>)?'
        r'(?P<ext>\..*?)$')
fn_pattern = re.compile(fn_pattern, re.I)


def numerateBN(bn, num=0, pat=fn_pattern):
    match = pat.match(bn)
    if match:
        groupdict = {
            k: v if v is not None else ''
            for k, v in match.groupdict().items()
        }
        return (groupdict['bn'] + "_%d" % num + groupdict['sep'] +
                groupdict['tok'] + groupdict['ext'])
    else:
        return bn + "_%d" % num


def anyNameClash(dirpath, bnames, key=op.exists):
    return any((key(op.join(dirpath, bn)) for bn in bnames))


def lowestConsecutiveUniqueFTN(dirpath, ftns, texs, key=op.exists):
    texs = list(texs)
    mapping = {}
    ftn_bns = [op.basename(ftn) for ftn in ftns]
    tex_bns = [op.basename(tex) for tex in texs]
    ftn_new_bns = ftn_bns
    tex_new_bns = tex_bns

    num = 0
    while anyNameClash(dirpath, tex_new_bns):
        num += 1
        tex_new_bns = [numerateBN(bn, num) for bn in tex_bns]
        ftn_new_bns = [numerateBN(bn, num) for bn in ftn_bns]

    mapping.update({
        texs[i]: op.join(dirpath, tex_new_bns[i])
        for i in range(len(tex_bns))
    })
    mapping.update({
        ftns[i]: op.join(dirpath, ftn_new_bns[i])
        for i in range(len(ftn_bns))
    })
    return mapping


lCUFTN = lowestConsecutiveUniqueFTN


def silentShellCall(command):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return subprocess.call(command, startupinfo=startupinfo)


def setReadOnly(path):
    if haveWritePermission(path if op.isdir(path) else op.dirname(path)):
        fileAtt = os.stat(path)[0]
        if (fileAtt & stat.S_IWRITE):
            os.chmod(path, stat.S_IREAD)
        else:
            pass
    else:
        pass


def purgeChar(string, pattern=r"\W", replace=""):
    return re.sub(r"[%s]" % pattern, replace, str(string))


def haveWritePermission(path, sub=False):
    '''
    @return: True if the user has write permission in *path*
             else False
    '''
    path = normpath(path)
    try:
        os.remove(getTemp(directory=path))
        return True
    except OSError, WindowsError:
        if sub:
            count = 1
            # check if the user has write permissions in subsequent subdirs
            for fl, fds, fls in os.walk(path):
                if count > 50:
                    break
                for fd in fds:
                    count += 1
                    try:
                        os.remove(getTemp(directory=op.join(fl, fd)))
                        return True
                    except (OSError, WindowsError):
                        continue
            return False
        else:
            return False


def scrollRight(self):
    # Doesn't belong here
    if self.pathScrollArea.width() < self.pathWidget.width():
        w = self.pathWidget.width() - self.pathScrollArea.width()
        q = w / 20
        if w % 20 > 0:
            q += 1
        self.pathWidget.scroll(-20 * q, 0)
        self.scrolled -= 20 * q


def pathSplitter(path, drive=False):
    '''
    splits a path and returns list of dir names
    @params:
            path: a valid path to some file or dir
            drive: list should include drive name or not (bool)
    '''
    if ":" in path:
        path = (":" + op.sep).join(path.split(":"))
    nodes = op.normpath(path if path else op.sep).split(op.sep)
    return nodes if drive else nodes[1:]


def longest_common_substring(s1, s2):
    set1 = set(s1[begin:end]
               for (begin,
                    end) in itertools.combinations(range(len(s1) + 1), 2))
    set2 = set(s2[begin:end]
               for (begin,
                    end) in itertools.combinations(range(len(s2) + 1), 2))
    common = set1.intersection(set2)
    maximal = [
        com for com in common
        if sum((s.find(com) for s in common)) == -1 * (len(common) - 1)
    ]
    return [(s, s1.index(s), s2.index(s)) for s in maximal]


def getParentWindowPos(parent, child, QtCore):
    parentCenter = QtCore.QPoint(parent.width() / 2, parent.height() / 2)
    childCenter = QtCore.QPoint(child.width() / 2, child.height() / 2)
    return parentCenter - childCenter


def getSequenceFiles(filepath):
    '''
    Get the sequence of files that are similar and exists in filename's
    directory. The sequence will be either negative or positive or both
    numerically increasing sequence.

    The function is a reverse engineered version of what Maya's file node
    uses for sequences.
    '''
    filename = normpath(filepath)
    dirname = op.dirname(filename)
    bname = op.basename(filename)
    filename, filext = op.splitext(bname)
    res = re.match(r'^(.*?)(\D)(-?\d*|<f>)$', filename)
    if not res:
        # Cannot be part of sequence of files
        return []
    # making match pattern for all the files in the sequence
    seqPattern = re.compile(('^' + ''.join(res.groups()[:-1]) + '(-?)(\\d+)' +
                             filext + '$').replace('.', '\\.'))
    # getting all the files from the directory and check whose names match the
    # sequence pattern
    return [
        normpath(os.path.join(dirname, dbn)) for dbn in os.listdir(dirname)
        if seqPattern.match(dbn)
    ] if os.path.exists(dirname) else []


def getUVTilePattern(filename, ext, filename_format='mari', filename2=''):
    flags = re.I
    if os.name == 'posix':
        flags = 0
    if filename_format == 'mari':
        return re.compile(('^' + filename + '(1\d{3})' + filename2 + ext +
                          '$').replace('.', '\\.'), flags)
    elif filename_format == 'mudbox':
        return re.compile((
            '^' + filename + '([uU][1-9]\d*_[vV][1-9]\d*)' + filename2 + ext +
            '$').replace('.', '\\.'), flags)
    elif filename_format == 'zbrush':
        return re.compile(
            ('^' + filename + '([uU]\d+_[vV]\d+)' + filename2 + ext +
                '$').replace('.', '\\.'), flags)
    return re.compile(('^' + filename + filename2 + ext + '$').replace('.',
                      '\\.'), flags)


udim_patterns = {
    'mari': re.compile('^(?P<filename>[^<]*)(?:\<UDIM\>)?'
                       '(?P<filename2>[^<]*)(?P<ext>\\..*?)$', re.I),
    'zbrush': re.compile('^(?P<filename>[^<]*)(?:[uU]\<U\>_[vV]\<V\>)?'
                         '(?P<filename2>[^<]*)(?P<ext>\\..*?)$', re.I),
    'mudbox': re.compile('^(?P<filename>[^<]*)(?:[uU]\<U\>_[vV]\<V\>)?'
                         '(?P<filename2>[^<]*)(?P<ext>\\..*?)$', re.I),
}

udim_detect_patterns = {
    'mari': re.compile('^(?P<filename>[^<]*)(?:\<UDIM\>)'
                       '(?P<filename2>[^<]*)(?P<ext>\\..*?)$', re.I),
    'zbrush': re.compile('^(?P<filename>[^<]*)(?:[uU]\<U\>_[vV]\<V\>)'
                         '(?P<filename2>[^<]*)(?P<ext>\\..*?)$', re.I),
    'mudbox': re.compile('^(?P<filename>[^<]*)(?:[uU]\<U\>_[vV]\<V\>)'
                         '(?P<filename2>[^<]*)(?P<ext>\\..*?)$', re.I),
}
udim_default_pattern = re.compile('^(?P<filename>[^<]*)(?P<filename2>[^<]*)'
                                  '(?P<ext>\\..*?)$')


def detectUdim(filepath):
    filepath = op.normpath(filepath)
    bname = op.basename(filepath)
    for name, pat in udim_detect_patterns.iteritems():
        match = pat.match(bname)
        if match:
            return name


def getUVTiles(filepath, filename_format='mari'):
    uvTiles = []
    filepath = op.normpath(filepath)
    dirname = op.dirname(filepath)
    bname = op.basename(filepath)
    udim_pattern = udim_patterns.get(filename_format, udim_default_pattern)
    match = udim_pattern.match(bname)
    if match:
        filename = match.group('filename')
        ext = match.group('ext')
        filename2 = match.group('filename2')
        tile_pattern = getUVTilePattern(
                filename, ext, filename_format, filename2)
        if op.exists(dirname):
            uvTiles = filter(op.exists, [
                normpath(os.path.join(dirname, dbn))
                for dbn in os.listdir(dirname) if tile_pattern.match(dbn)
            ])
    return uvTiles


def getTxFile(filepath, ext='tx'):
    '''
    Get the sequence of files that are named similar but with extension '.tx'
    '''
    filename = normpath(filepath)
    dirname = op.dirname(filename)
    bname = op.basename(filename)
    filename, fileext = op.splitext(bname)
    txPattern = re.compile(r'\.%s' % ext, re.IGNORECASE)
    if not txPattern.match(fileext):
        txFilename = op.join(dirname, filename + r'.%s' % ext)
        if op.exists(txFilename):
            return txFilename
    return None


getFileByExtension = getTxFile


def copyFilesTo(desPath, files=[]):
    copiedTo = []
    if not op.exists(desPath) or not op.isdir(desPath):
        return copiedTo
    for fl in files:
        if op.isfile(fl) and op.exists(fl):
            desFile = op.join(desPath,
                              lCUFN(
                                  desPath,
                                  op.basename(fl),
                                  hasExt=True,
                                  key=op.exists))
            shutil.copy2(fl, desFile)
            copiedTo.append(desFile)
        else:
            return copiedTo
    return copiedTo


def lower(ls=[]):
    '''
    @ls: list of strings
    @return: all the string lowercased in the form of a generator
    '''
    try:
        return ((string.lower() for string in ls)
                if isinstance(ls, list) else (ls.lower() if isinstance(
                    ls, basestring) else ls))
    except BaseException as e:
        print e


def isDirInPath(dir, path):
    '''
    @return: True if the "dir" is in "path", else returns False
    '''
    dirs = pathSplitter(path)
    dirs = [str(x.lower()) for x in dirs]
    if str(dir.lower()) in dirs:
        return True
    else:
        return False


def gotoLocation(path):
    path = normpath(path)
    if os.name == 'nt':
        subprocess.Popen('explorer /select' + ',' + path)
    else:
        # http://askubuntu.com/q/23596/44293
        subprocess.Popen('xdg-open ' + path)


def getFileMDate(path):
    return str(
        datetime.datetime.fromtimestamp(op.getmtime(path))).split('.')[0]


def timestampToDateTime(timestamp):
    return str(datetime.datetime.fromtimestamp(timestamp)).split('.')[0]


def profile(sort='cumulative', lines=50, strip_dirs=False):
    """A decorator which profiles a callable.
    Example usage:

    >>> @profile
        def factorial(n):
            n = abs(int(n))
            if n < 1:
                    n = 1
            x = 1
            for i in range(1, n + 1):
                    x = i * x
            return x
    ...
    >>> factorial(5)
    Thu Jul 15 20:58:21 2010    /tmp/tmpIDejr5

             4 function calls in 0.000 CPU seconds

       Ordered by: internal time, call count

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
            1    0.000    0.000    0.000    0.000 profiler.py:120(factorial)
            1    0.000    0.000    0.000    0.000 {range}
            1    0.000    0.000    0.000    0.000 {abs}

    120
    >>>
    """

    def outer(fun):
        def inner(*args, **kwargs):
            file = tempfile.NamedTemporaryFile(delete=False)
            prof = cProfile.Profile()
            try:
                ret = prof.runcall(fun, *args, **kwargs)
            except:
                file.close()
                raise

            prof.print_stats()
            # stats = pstats.Stats(file.name)
            # if strip_dirs:
            #     stats.strip_dirs()
            # if isinstance(sort, (tuple, list)):
            #     stats.sort_stats(*sort)
            # else:
            #     stats.sort_stats(sort)
            # stats.print_stats(lines)

            return ret

        return inner

    # in case this is defined as "@profile" instead of "@profile()"
    if hasattr(sort, '__call__'):
        fun = sort
        sort = 'cumulative'
        outer = outer(fun)
    return outer


def getDirs(path):

    if path and op.exists(path):
        return os.listdir(path)


def timeMe(func):
    def wrapper(*args, **kwargs):
        t = time.time()
        result = func(*args, **kwargs)
        print time.time() - t
        return result

    return wrapper


@timeMe
def sha512OfFile(path):
    if not op.exists(path):
        raise Exception
    with open(path, "rb") as testFile:
        hash = hashlib.sha512()
        while True:
            piece = testFile.read(1024**3)
            if piece:
                hash.update(piece)
            else:
                hex_hash = hash.hexdigest()
                break
    return hex_hash


def clearList(lis):
    try:
        del lis[:]
    except:
        return False


def which(cmd, mode=os.F_OK | os.X_OK, path=None):
    """Given a command, mode, and a PATH string, return the path which
    conforms to the given mode on the PATH, or None if there is no such
    file.

    `mode` defaults to os.F_OK | os.X_OK. `path` defaults to the result
    of os.environ.get("PATH"), or can be overridden with a custom search
    path.

    """

    # Check that a given file can be accessed with the correct mode.
    # Additionally check that `file` is not a directory, as on Windows
    # directories pass the os.access check.
    def _access_check(fn, mode):
        return (os.path.exists(fn) and os.access(fn, mode) and
                not os.path.isdir(fn))

    # Short circuit. If we're given a full path which matches the mode
    # and it exists, we're done here.
    if _access_check(cmd, mode):
        return cmd

    path = (path or os.environ.get("PATH", os.defpath)).split(os.pathsep)

    if sys.platform == "win32":
        # The current directory takes precedence on Windows.
        if os.curdir not in path:
            path.insert(0, os.curdir)

        pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
        matches = [cmd for ext in pathext if cmd.lower().endswith(ext.lower())]
        files = [cmd] if matches else [cmd + ext.lower() for ext in pathext]
    else:
        files = [cmd]

    seen = set()
    for dir in path:
        dir = os.path.normcase(dir)
        if dir not in seen:
            seen.add(dir)
            for thefile in files:
                name = os.path.join(dir, thefile)
                if _access_check(name, mode):
                    return name
    return None


if __name__ == "__main__":
    print __name__
