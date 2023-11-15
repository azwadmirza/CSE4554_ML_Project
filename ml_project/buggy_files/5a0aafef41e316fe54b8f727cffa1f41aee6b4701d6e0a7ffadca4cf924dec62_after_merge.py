def update_prefix(path, new_prefix, placeholder=prefix_placeholder, mode='text'):
    if on_win:
        # force all prefix replacements to forward slashes to simplify need to escape backslashes
        # replace with unix-style path separators
        new_prefix = new_prefix.replace('\\', '/')

    path = os.path.realpath(path)
    with open(path, 'rb') as fi:
        original_data = data = fi.read()

    data = replace_prefix(mode, data, placeholder, new_prefix)
    if not on_win:
        data = replace_long_shebang(mode, data)

    if data == original_data:
        return
    st = os.lstat(path)
    # Remove file before rewriting to avoid destroying hard-linked cache
    os.remove(path)
    with exp_backoff_fn(open, path, 'wb') as fo:
        fo.write(data)
    os.chmod(path, stat.S_IMODE(st.st_mode))