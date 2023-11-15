def _fs_to_record_path(path, relative_to=None):
    # type: (text_type, Optional[text_type]) -> RecordPath
    if relative_to is not None:
        path = os.path.relpath(path, relative_to)
    path = path.replace(os.path.sep, '/')
    return cast('RecordPath', path)