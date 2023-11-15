def normexe(orig):
    def _error(msg):
        raise ExecutableNotFoundError('Executable `{}` {}'.format(orig, msg))

    if os.sep not in orig and (not os.altsep or os.altsep not in orig):
        exe = find_executable(orig)
        if exe is None:
            _error('not found')
        return exe
    elif not os.access(orig, os.X_OK):
        _error('not found')
    elif os.path.isdir(orig):
        _error('is a directory')
    else:
        return orig