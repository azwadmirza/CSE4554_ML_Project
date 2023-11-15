def __shred_sqlite_char_columns(table, cols=None, where=""):
    """Create an SQL command to shred character columns"""
    cmd = ""
    if cols and options.get('shred'):
        cmd += "update or ignore %s set %s %s;" % \
            (table, ",".join(["%s = randomblob(length(%s))" % (col, col)
                              for col in cols]), where)
        cmd += "update or ignore %s set %s %s;" % \
            (table, ",".join(["%s = zeroblob(length(%s))" % (col, col)
                              for col in cols]), where)
    cmd += "delete from %s %s;" % (table, where)
    return cmd