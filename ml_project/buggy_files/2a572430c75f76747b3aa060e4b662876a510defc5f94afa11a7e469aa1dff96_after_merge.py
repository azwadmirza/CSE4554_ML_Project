def _open_log_file(filename):
    """
    Helper to open the log file (always in the log dir) and cache its
    handle.  Will create a new file in the log dir if one didn't
    exist.

    To avoid keeping the filehandle open indefinitely we reset it every
    _LOG_FILE_HANDLE_RESET accesses. This may help resolve issues for very
    long uptimes and heavy log use.

    """
    # we delay import of settings to keep logger module as free
    # from django as possible.
    global _LOG_FILE_HANDLES, _LOG_FILE_HANDLE_COUNTS, _LOGDIR, _LOG_ROTATE_SIZE
    if not _LOGDIR:
        from django.conf import settings
        _LOGDIR = settings.LOG_DIR
        _LOG_ROTATE_SIZE = settings.CHANNEL_LOG_ROTATE_SIZE

    filename = os.path.join(_LOGDIR, filename)
    if filename in _LOG_FILE_HANDLES:
        _LOG_FILE_HANDLE_COUNTS[filename] += 1
        if _LOG_FILE_HANDLE_COUNTS[filename] > _LOG_FILE_HANDLE_RESET:
            # close/refresh handle
            _LOG_FILE_HANDLES[filename].close()
            del _LOG_FILE_HANDLES[filename]
        else:
            # return cached handle
            return _LOG_FILE_HANDLES[filename]
    try:
        filehandle = EvenniaLogFile.fromFullPath(filename, rotateLength=_LOG_ROTATE_SIZE)
        # filehandle = open(filename, "a+")  # append mode + reading
        _LOG_FILE_HANDLES[filename] = filehandle
        _LOG_FILE_HANDLE_COUNTS[filename] = 0
        return filehandle
    except IOError:
        log_trace()
    return None