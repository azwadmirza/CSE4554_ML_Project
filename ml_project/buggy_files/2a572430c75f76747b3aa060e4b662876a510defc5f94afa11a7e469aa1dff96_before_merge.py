def _open_log_file(filename):
    """
    Helper to open the log file (always in the log dir) and cache its
    handle.  Will create a new file in the log dir if one didn't
    exist.
    """
    # we delay import of settings to keep logger module as free
    # from django as possible.
    global _LOG_FILE_HANDLES, _LOGDIR, _LOG_ROTATE_SIZE
    if not _LOGDIR:
        from django.conf import settings
        _LOGDIR = settings.LOG_DIR
        _LOG_ROTATE_SIZE = settings.CHANNEL_LOG_ROTATE_SIZE

    filename = os.path.join(_LOGDIR, filename)
    if filename in _LOG_FILE_HANDLES:
        # cache the handle
        return _LOG_FILE_HANDLES[filename]
    else:
        try:
            filehandle = EvenniaLogFile.fromFullPath(filename, rotateLength=_LOG_ROTATE_SIZE)
            # filehandle = open(filename, "a+")  # append mode + reading
            _LOG_FILE_HANDLES[filename] = filehandle
            return filehandle
        except IOError:
            log_trace()
    return None