def pycmd2argv(cmd):
    r"""Take the path of a python command and return a list (argv-style).

    This only works on Python based command line programs and will find the
    location of the ``python`` executable using ``sys.executable`` to make
    sure the right version is used.

    For a given path ``cmd``, this returns [cmd] if cmd's extension is .exe,
    .com or .bat, and [, cmd] otherwise.

    Parameters
    ----------
    cmd : string
      The path of the command.

    Returns
    -------
    argv-style list.
    """
    ext = os.path.splitext(cmd)[1]
    if ext in ['.exe', '.com', '.bat']:
        return [cmd]
    else:
        if sys.platform == 'win32':
            # The -u option here turns on unbuffered output, which is required
            # on Win32 to prevent wierd conflict and problems with Twisted.
            # Also, use sys.executable to make sure we are picking up the
            # right python exe.
            return [sys.executable, '-u', cmd]
        else:
            return [sys.executable, cmd]