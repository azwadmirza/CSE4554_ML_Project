def sanitize_filename(name, rootDir=None):
    '''Replace reserved character/name with underscore (windows), rootDir is not sanitized.'''
    # get the absolute rootdir
    if rootDir is not None:
        rootDir = os.path.abspath(rootDir)

    # Unescape '&amp;', '&lt;', and '&gt;'
    name = html.unescape(name)

    name = __badchars__.sub("_", name)

    # Remove unicode control characters
    name = "".join(c for c in name if unicodedata.category(c) != "Cc")

    # Strip leading/trailing space for each directory
    # Issue #627: remove trailing '.'
    # Ensure Windows reserved filenames are prefixed with _
    stripped_name = list()
    for item in name.split(os.sep):
        if Path(item).is_reserved():
            item = '_' + item
        stripped_name.append(item.strip(" .\t\r\n"))
    name = os.sep.join(stripped_name)

    if platform.system() == 'Windows':
        # cut whole path to 255 char
        # TODO: check for Windows long path extensions being enabled
        if rootDir is not None:
            # need to remove \\ from name prefix
            tname = name[1:] if name[0] == "\\" else name
            full_name = os.path.abspath(os.path.join(rootDir, tname))
        else:
            full_name = os.path.abspath(name)

        if len(full_name) > 255:
            filename, extname = os.path.splitext(name)  # NOT full_name, to avoid clobbering paths
            # don't trim the extension
            name = filename[:255 - len(extname)] + extname
            if name == extname:  # we have no file name left
                raise OSError(None, "Path name too long", full_name, 0x000000A1)  # 0xA1 is "invalid path"
    else:
        # Unix: cut filename to <= 249 bytes
        # TODO: allow macOS higher limits, HFS+ allows 255 UTF-16 chars, and APFS 255 UTF-8 chars
        while len(name.encode('utf-8')) > 249:
            filename, extname = os.path.splitext(name)
            name = filename[:len(filename) - 1] + extname

    if rootDir is not None:
        name = name[1:] if name[0] == "\\" else name
        # name = os.path.abspath(os.path.join(rootDir, name))
        # compatibility...
        name = rootDir + os.sep + name

    get_logger().debug("Sanitized Filename: %s", name)

    return name