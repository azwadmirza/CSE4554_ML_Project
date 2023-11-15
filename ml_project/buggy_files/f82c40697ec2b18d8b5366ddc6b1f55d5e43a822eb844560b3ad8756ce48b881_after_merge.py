def _setup_crud_params(compiler, stmt, local_stmt_type, **kw):
    restore_isinsert = compiler.isinsert
    restore_isupdate = compiler.isupdate
    restore_isdelete = compiler.isdelete

    should_restore = (
        (restore_isinsert or restore_isupdate or restore_isdelete)
        or len(compiler.stack) > 1
        or "visiting_cte" in kw
    )

    if local_stmt_type is ISINSERT:
        compiler.isupdate = False
        compiler.isinsert = True
    elif local_stmt_type is ISUPDATE:
        compiler.isupdate = True
        compiler.isinsert = False
    elif local_stmt_type is ISDELETE:
        if not should_restore:
            compiler.isdelete = True
    else:
        assert False, "ISINSERT, ISUPDATE, or ISDELETE expected"

    try:
        if local_stmt_type in (ISINSERT, ISUPDATE):
            return _get_crud_params(compiler, stmt, **kw)
    finally:
        if should_restore:
            compiler.isinsert = restore_isinsert
            compiler.isupdate = restore_isupdate
            compiler.isdelete = restore_isdelete