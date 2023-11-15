def trash_free_desktop(path):
    """Partial implementation of
    http://www.freedesktop.org/wiki/Specifications/trash-spec

    This doesn't work for files in the trash directory.
    """

    path = abspath(path)

    if not exists(path):
        raise TrashError("Path %s does not exist." % path)

    trash_dir = abspath(get_fd_trash_dir(path))

    # to make things easier
    if path.startswith(join(trash_dir, "")) or path == trash_dir:
        raise TrashError("Can't move files to the trash from within the"
                         "trash directory.")

    files = join(trash_dir, "files")
    info = join(trash_dir, "info")

    for d in (files, info):
        if not isdir(d):
            os.makedirs(d, 0o700)

    info_ext = ".trashinfo"
    name = basename(path)
    flags = os.O_EXCL | os.O_CREAT | os.O_WRONLY
    mode = 0o644
    try:
        info_path = join(info, name + info_ext)
        info_fd = os.open(info_path, flags, mode)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
        i = 2
        while 1:
            head, tail = splitext(name)
            temp_name = "%s.%d%s" % (head, i, tail)
            info_path = join(info, temp_name + info_ext)
            try:
                info_fd = os.open(info_path, flags, mode)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                i += 1
                continue
            name = temp_name
            break

    parent = dirname(trash_dir)
    if path.startswith(join(parent, "")):
        norm_path = path[len(join(parent, "")):]
    else:
        norm_path = path

    del_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())

    data = "[Trash Info]\n"
    data += "Path=%s\n" % urllib.pathname2url(norm_path)
    data += "DeletionDate=%s\n" % del_date
    os.write(info_fd, data)
    os.close(info_fd)

    target_path = join(files, name)
    try:
        shutil.move(path, target_path)
    except OSError:
        os.unlink(info_path)
        raise