def RORP2Record(rorpath):
    """From RORPath, return text record of file's metadata"""
    str_list = [b"File %s\n" % quote_path(rorpath.get_indexpath())]

    # Store file type, e.g. "dev", "reg", or "sym", and type-specific data
    type = rorpath.gettype()
    if type is None:
        type = "None"
    str_list.append(b"  Type %b\n" % type.encode('ascii'))
    if type == "reg":
        str_list.append(b"  Size %i\n" % rorpath.getsize())

        # If there is a resource fork, save it.
        if rorpath.has_resource_fork():
            if not rorpath.get_resource_fork():
                rf = b"None"
            else:
                rf = binascii.hexlify(rorpath.get_resource_fork())
            str_list.append(b"  ResourceFork %b\n" % (rf, ))

        # If there is Carbon data, save it.
        if rorpath.has_carbonfile():
            cfile = carbonfile2string(rorpath.get_carbonfile())
            str_list.append(b"  CarbonFile %b\n" % (cfile, ))

        # If file is hardlinked, add that information
        if Globals.preserve_hardlinks != 0:
            numlinks = rorpath.getnumlinks()
            if numlinks > 1:
                str_list.append(b"  NumHardLinks %i\n" % numlinks)
                str_list.append(b"  Inode %i\n" % rorpath.getinode())
                str_list.append(b"  DeviceLoc %i\n" % rorpath.getdevloc())

        # Save any hashes, if available
        if rorpath.has_sha1():
            str_list.append(
                b'  SHA1Digest %b\n' % rorpath.get_sha1().encode('ascii'))

    elif type == "None":
        return b"".join(str_list)
    elif type == "dir" or type == "sock" or type == "fifo":
        pass
    elif type == "sym":
        str_list.append(b"  SymData %b\n" % quote_path(rorpath.readlink()))
    elif type == "dev":
        major, minor = rorpath.getdevnums()
        if rorpath.isblkdev():
            devchar = "b"
        else:
            assert rorpath.ischardev()
            devchar = "c"
        str_list.append(
            b"  DeviceNum %b %i %i\n" % (devchar.encode(), major, minor))

    # Store time information
    if type != 'sym' and type != 'dev':
        str_list.append(b"  ModTime %i\n" % rorpath.getmtime())

    # Add user, group, and permission information
    uid, gid = rorpath.getuidgid()
    str_list.append(b"  Uid %i\n" % uid)
    str_list.append(b"  Uname %b\n" % (rorpath.getuname() or ":").encode())
    str_list.append(b"  Gid %i\n" % gid)
    str_list.append(b"  Gname %b\n" % (rorpath.getgname() or ":").encode())
    str_list.append(b"  Permissions %d\n" % rorpath.getperms())

    # Add long filename information
    if rorpath.has_alt_mirror_name():
        str_list.append(
            b"  AlternateMirrorName %b\n" % (rorpath.get_alt_mirror_name(), ))
    elif rorpath.has_alt_inc_name():
        str_list.append(
            b"  AlternateIncrementName %b\n" % (rorpath.get_alt_inc_name(), ))

    return b"".join(str_list)