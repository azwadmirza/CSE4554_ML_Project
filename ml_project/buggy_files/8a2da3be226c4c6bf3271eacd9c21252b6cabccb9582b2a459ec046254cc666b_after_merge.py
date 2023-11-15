def delete_chrome_history(path):
    """Clean history from History and Favicon files without affecting bookmarks"""
    if not os.path.exists(path):
        logger.debug('aborting delete_chrome_history() because history does not exist: %s' % path)
        return
    cols = ('url', 'title')
    where = ""
    ids_int = get_chrome_bookmark_ids(path)
    if ids_int:
        ids_str = ",".join([str(id0) for id0 in ids_int])
        where = "where id not in (%s) " % ids_str
    cmds = __shred_sqlite_char_columns('urls', cols, where)
    cmds += __shred_sqlite_char_columns('visits')
    # Google Chrome 79 no longer has lower_term in keyword_search_terms
    cols = ('term',)
    cmds += __shred_sqlite_char_columns('keyword_search_terms', cols)
    ver = __get_chrome_history(path)
    if ver >= 20:
        # downloads, segments, segment_usage first seen in Chrome 14,
        #   Google Chrome 15 (database version = 20).
        # Google Chrome 30 (database version 28) doesn't have full_path, but it
        # does have current_path and target_path
        if ver >= 28:
            cmds += __shred_sqlite_char_columns(
                'downloads', ('current_path', 'target_path'))
            cmds += __shred_sqlite_char_columns(
                'downloads_url_chains', ('url', ))
        else:
            cmds += __shred_sqlite_char_columns(
                'downloads', ('full_path', 'url'))
        cmds += __shred_sqlite_char_columns('segments', ('name',))
        cmds += __shred_sqlite_char_columns('segment_usage')
    FileUtilities.execute_sqlite3(path, cmds)