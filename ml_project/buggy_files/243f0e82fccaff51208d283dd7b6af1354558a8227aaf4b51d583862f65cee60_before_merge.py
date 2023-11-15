def copy(rpin, rpout, compress=0):
    """Copy RPath rpin to rpout.  Works for symlinks, dirs, etc.

    Returns close value of input for regular file, which can be used
    to pass hashes on.

    """
    log.Log("Regular copying %s to %s" % (rpin.index, rpout.get_safepath()), 6)
    if not rpin.lstat():
        if rpout.lstat():
            rpout.delete()
        return

    if rpout.lstat():
        if rpin.isreg() or not cmp(rpin, rpout):
            rpout.delete()  # easier to write than compare
        else:
            return

    if rpin.isreg():
        return copy_reg_file(rpin, rpout, compress)
    elif rpin.isdir():
        rpout.mkdir()
    elif rpin.issym():
        # some systems support permissions for symlinks, but
        # only by setting at creation via the umask
        if Globals.symlink_perms:
            orig_umask = os.umask(0o777 & ~rpin.getperms())
        rpout.symlink(rpin.readlink())
        if Globals.symlink_perms:
            os.umask(orig_umask)  # restore previous umask
    elif rpin.ischardev():
        major, minor = rpin.getdevnums()
        rpout.makedev("c", major, minor)
    elif rpin.isblkdev():
        major, minor = rpin.getdevnums()
        rpout.makedev("b", major, minor)
    elif rpin.isfifo():
        rpout.mkfifo()
    elif rpin.issock():
        rpout.mksock()
    else:
        raise RPathException("File '%s' has unknown type." % rpin.get_safepath())