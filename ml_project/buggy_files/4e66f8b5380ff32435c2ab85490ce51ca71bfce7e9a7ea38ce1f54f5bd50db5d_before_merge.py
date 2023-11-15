def delete_chrome_favicons(path):
    """Delete Google Chrome and Chromium favicons not use in in history for bookmarks"""

    path_history = os.path.join(os.path.dirname(path), 'History')
    ver = __get_chrome_history(path)
    cmds = ""

    if ver >= 4:
        # Version 4 includes Chromium 12
        # Version 20 includes Chromium 14, Google Chrome 15, Google Chrome 19
        # Version 22 includes Google Chrome 20
        # Version 25 is Google Chrome 26
        # Version 26 is Google Chrome 29
        # Version 28 is Google Chrome 30
        # Version 29 is Google Chrome 37
        # Version 32 is Google Chrome 51
        # Version 36 is Google Chrome 60
        # Version 38 is Google Chrome 64

        # icon_mapping
        cols = ('page_url',)
        where = None
        if os.path.exists(path_history):
            cmds += "attach database \"%s\" as History;" % path_history
            where = "where page_url not in (select distinct url from History.urls)"
        cmds += __shred_sqlite_char_columns('icon_mapping', cols, where)

        # favicon images
        cols = ('image_data', )
        where = "where icon_id not in (select distinct icon_id from icon_mapping)"
        cmds += __shred_sqlite_char_columns('favicon_bitmaps', cols, where)

        # favicons
        # Google Chrome 30 (database version 28): image_data moved to table
        # favicon_bitmaps
        if ver < 28:
            cols = ('url', 'image_data')
        else:
            cols = ('url', )
        where = "where id not in (select distinct icon_id from icon_mapping)"
        cmds += __shred_sqlite_char_columns('favicons', cols, where)
    elif 3 == ver:
        # Version 3 includes Google Chrome 11

        cols = ('url', 'image_data')
        where = None
        if os.path.exists(path_history):
            cmds += "attach database \"%s\" as History;" % path_history
            where = "where id not in(select distinct favicon_id from History.urls)"
        cmds += __shred_sqlite_char_columns('favicons', cols, where)
    else:
        raise RuntimeError('%s is version %d' % (path, ver))

    FileUtilities.execute_sqlite3(path, cmds)