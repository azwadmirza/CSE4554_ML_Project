def is_fs_case_sensitive():
    global _FS_CASE_SENSITIVE

    if _FS_CASE_SENSITIVE is None:
        with tempfile.NamedTemporaryFile(prefix="TmP") as tmp_file:
            _FS_CASE_SENSITIVE = not os.path.exists(tmp_file.name.lower())
            logging.debug(
                "filesystem under is %r%s case-sensitive", tmp_file.name, "" if _FS_CASE_SENSITIVE else " not"
            )
    return _FS_CASE_SENSITIVE