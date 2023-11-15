def create_archive(root, files=None, fileobj=None, gzip=False):
    if not fileobj:
        fileobj = tempfile.NamedTemporaryFile()
    t = tarfile.open(mode='w:gz' if gzip else 'w', fileobj=fileobj)
    if files is None:
        files = build_file_list(root)
    for path in files:
        full_path = os.path.join(root, path)

        if os.lstat(full_path).st_mode & os.R_OK == 0:
            raise IOError(
                'Can not access file in context: {}'.format(full_path)
            )
        i = t.gettarinfo(full_path, arcname=path)
        if i is None:
            # This happens when we encounter a socket file. We can safely
            # ignore it and proceed.
            continue

        # Workaround https://bugs.python.org/issue32713
        if i.mtime < 0 or i.mtime > 8**11 - 1:
            i.mtime = int(i.mtime)

        if constants.IS_WINDOWS_PLATFORM:
            # Windows doesn't keep track of the execute bit, so we make files
            # and directories executable by default.
            i.mode = i.mode & 0o755 | 0o111

        if i.isfile():
            try:
                with open(full_path, 'rb') as f:
                    t.addfile(i, f)
            except IOError:
                t.addfile(i, None)
        else:
            # Directories, FIFOs, symlinks... don't need to be read.
            t.addfile(i, None)
    t.close()
    fileobj.seek(0)
    return fileobj