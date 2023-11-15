def make_file_dict(filename):
    """Generate the data dictionary for the given RPath

    This is a global function so that os.name can be called locally,
    thus avoiding network lag and so that we only need to send the
    filename over the network, thus avoiding the need to pickle an
    (incomplete) rpath object.
    """

    def _readlink(filename):
        """FIXME wrapper function to workaround a bug in os.readlink on Windows
        not accepting bytes path. This function can be removed once pyinstaller
        supports Python 3.8 and a new release can be made.
        See https://github.com/pyinstaller/pyinstaller/issues/4311
        """

        if os.name == 'nt' and not isinstance(filename, str):
            # we assume a bytes representation
            return os.fsencode(os.readlink(os.fsdecode(filename)))
        else:
            return os.readlink(filename)

    try:
        statblock = os.lstat(filename)
    except (FileNotFoundError, NotADirectoryError):
        # FIXME not sure if this shouldn't trigger a warning but doing it
        # generates (too) many messages during the tests
        # log.Log("Warning: missing file '%s' couldn't be assessed." % filename, 2)
        return {'type': None}
    data = {}
    mode = statblock[stat.ST_MODE]

    if stat.S_ISREG(mode):
        type_ = 'reg'
    elif stat.S_ISDIR(mode):
        type_ = 'dir'
    elif stat.S_ISCHR(mode):
        type_ = 'dev'
        s = statblock.st_rdev
        data['devnums'] = ('c', os.major(s), os.minor(s))
    elif stat.S_ISBLK(mode):
        type_ = 'dev'
        s = statblock.st_rdev
        data['devnums'] = ('b', os.major(s), os.minor(s))
    elif stat.S_ISFIFO(mode):
        type_ = 'fifo'
    elif stat.S_ISLNK(mode):
        type_ = 'sym'
        # FIXME reverse once Python 3.8 can be used under Windows
        # data['linkname'] = os.readlink(filename)
        data['linkname'] = _readlink(filename)
    elif stat.S_ISSOCK(mode):
        type_ = 'sock'
    else:
        raise C.UnknownFileError(filename)
    data['type'] = type_
    data['size'] = statblock[stat.ST_SIZE]
    data['perms'] = stat.S_IMODE(mode)
    data['uid'] = statblock[stat.ST_UID]
    data['gid'] = statblock[stat.ST_GID]
    data['inode'] = statblock[stat.ST_INO]
    data['devloc'] = statblock[stat.ST_DEV]
    data['nlink'] = statblock[stat.ST_NLINK]

    if os.name == 'nt':
        try:
            attribs = win32api.GetFileAttributes(os.fsdecode(filename))
        except pywintypes.error as exc:
            if (exc.args[0] == 32):  # file in use
                # we could also ignore with: return {'type': None}
                # but this approach seems to be better handled
                attribs = 0
            else:
                # we replace the specific Windows exception by a generic
                # one also understood by a potential Linux client/server
                raise OSError(None, exc.args[1] + " - " + exc.args[2],
                              filename, exc.args[0]) from None
        if attribs & win32con.FILE_ATTRIBUTE_REPARSE_POINT:
            data['type'] = 'sym'
            data['linkname'] = None

    if not (type_ == 'sym' or type_ == 'dev'):
        # mtimes on symlinks and dev files don't work consistently
        data['mtime'] = int(statblock[stat.ST_MTIME])
        data['atime'] = int(statblock[stat.ST_ATIME])
        data['ctime'] = int(statblock[stat.ST_CTIME])
    return data