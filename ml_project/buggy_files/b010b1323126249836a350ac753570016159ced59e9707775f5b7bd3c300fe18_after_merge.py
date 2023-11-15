def _get_root_dirs():
    if not app.ROOT_DIRS:
        return {}

    root_dir = {}
    default_index = int(app.ROOT_DIRS[0])
    root_dir['default_index'] = default_index
    # clean up the list: replace %xx escapes with single-character equivalent
    # and remove default_index value from list (this fixes the offset)
    root_dirs = [
        unquote_plus(x)
        for x in app.ROOT_DIRS[1:]
    ]

    try:
        default_dir = root_dirs[default_index]
    except IndexError:
        return {}

    dir_list = []
    for root_dir in root_dirs:
        valid = 1
        try:
            os.listdir(root_dir)
        except OSError:
            valid = 0
        default = 0
        if root_dir is default_dir:
            default = 1

        cur_dir = {
            'valid': valid,
            'location': root_dir,
            'default': default
        }
        dir_list.append(cur_dir)

    return dir_list