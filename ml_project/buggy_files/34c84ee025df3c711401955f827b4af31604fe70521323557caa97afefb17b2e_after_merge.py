def _fs_to_record_path(path, relative_to=None):
    # type: (text_type, Optional[text_type]) -> RecordPath
    if relative_to is not None:
        # On Windows, do not handle relative paths if they belong to different
        # logical disks
        if os.path.splitdrive(path)[0].lower() == \
                os.path.splitdrive(relative_to)[0].lower():
            path = os.path.relpath(path, relative_to)
    path = path.replace(os.path.sep, '/')
    return cast('RecordPath', path)