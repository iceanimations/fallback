import sys
import shutil
import os
import traceback
import logging


logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def copytree(src, dst, symlinks=False, ignore=None):
    """Recursively copy a directory tree using copy2().

    The destination directory must not already exist.
    If exception(s) occur, an Error is raised with a list of reasons.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.

    The optional ignore argument is a callable. If given, it
    is called with the `src` parameter, which is the directory
    being visited by copytree(), and `names` which is the list of
    `src` contents, as returned by os.listdir():

        callable(src, names) -> ignored_names

    Since copytree() is called recursively, the callable will be
    called once for each directory that is copied. It returns a
    list of names relative to the `src` directory that should
    not be copied.

    XXX Consider this example code rather than the ultimate tool.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                logging.info(srcname)
                shutil.copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error, err:
            errors.extend(err.args[0])
        except EnvironmentError, why:
            errors.append((srcname, dstname, str(why)))
    try:
        shutil.copystat(src, dst)
    except OSError, why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.append((src, dst, str(why)))
    if errors:
        raise shutil.Error, errors

try:
    fromdir = sys.argv[1]
    todir = sys.argv[2]

    copy = shutil.copy2

    tree = False
    if '--tree' in sys.argv[3:]:
        tree = True
        copy = shutil.copytree

    fromfiles = [fromdir]
    if os.path.isdir(fromdir):
        if tree:
            copy = copytree
        else:
            fromfiles = [
                    os.path.join(fromdir, f)
                    for f in os.listdir(fromdir)
                    if os.path.isfile(os.path.join(fromdir, f))]

    if os.path.isfile(todir) and len(fromfiles) > 1:
        todir = os.path.dirname(todir)

    for fromfile in fromfiles:
        copy(fromfile, todir)

except BaseException as be:
    err = traceback.format_exc()
    sys.stderr.write(err)
    sys.exit(be.errno)
