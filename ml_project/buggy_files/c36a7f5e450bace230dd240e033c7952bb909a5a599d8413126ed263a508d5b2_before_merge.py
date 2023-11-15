def update_file_if_changed(c, file_name, temp_name):
    """Compares two files.

    If they are different, we replace file_name with temp_name.
    Otherwise, we just delete temp_name. Both files should be closed."""
    if g.os_path_exists(file_name):
        if filecmp.cmp(temp_name, file_name):
            kind = 'unchanged'
            ok = g.utils_remove(temp_name)
        else:
            kind = '***updating'
            mode = g.utils_stat(file_name)
            ok = g.utils_rename(c, temp_name, file_name, mode)
    else:
        kind = 'creating'
        # 2010/02/04: g.utils_rename no longer calls
        # makeAllNonExistentDirectories
        head, tail = g.os_path_split(file_name)
        ok = True
        if head:
            ok = g.makeAllNonExistentDirectories(head, c=c)
        if ok:
            ok = g.utils_rename(c, temp_name, file_name)
    if ok:
        g.es('', f'{kind:12}: {file_name}')
    else:
        g.error("rename failed: no file created!")
        g.es('', file_name, " may be read-only or in use")