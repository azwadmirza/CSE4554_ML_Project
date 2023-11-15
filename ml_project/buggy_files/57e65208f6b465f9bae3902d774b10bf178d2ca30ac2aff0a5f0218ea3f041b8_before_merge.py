def touch(path, mkdir=False, sudo_safe=False):
    # sudo_safe: use any time `path` is within the user's home directory
    # returns:
    #   True if the file did not exist but was created
    #   False if the file already existed
    # raises: permissions errors such as EPERM and EACCES
    path = expand(path)
    log.trace("touching path %s", path)
    if lexists(path):
        utime(path, None)
        return True
    else:
        dirpath = dirname(path)
        if not isdir(dirpath) and mkdir:
            if sudo_safe:
                mkdir_p_sudo_safe(dirpath)
            else:
                mkdir_p(dirpath)
        else:
            assert isdir(dirname(path))
        try:
            fh = open(path, 'a')
        except:
            raise
        else:
            fh.close()
            if sudo_safe and not on_win and os.environ.get('SUDO_UID') is not None:
                uid = int(os.environ['SUDO_UID'])
                gid = int(os.environ.get('SUDO_GID', -1))
                log.trace("chowning %s:%s %s", uid, gid, path)
                os.chown(path, uid, gid)
            return False