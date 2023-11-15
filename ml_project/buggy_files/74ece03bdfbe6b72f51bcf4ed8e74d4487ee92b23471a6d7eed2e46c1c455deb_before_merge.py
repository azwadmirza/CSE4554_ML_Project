def expands_symlinks_for_windows():
    """replaces the symlinked files with a copy of the original content.

    In windows (msysgit), a symlink is converted to a text file with a
    path to the file it points to. If not corrected, installing from a git
    clone will end with some files with bad content

    After install the working copy  will be dirty (symlink markers rewroted with
    real content)
    """
    if sys.platform != 'win32':
        return

    # apply the fix
    localdir = os.path.dirname(os.path.abspath(__file__))
    oldpath = sys.path[:]
    sys.path.insert(0, os.path.join(localdir, 'nikola'))
    winutils = __import__('winutils')
    failures = winutils.fix_all_git_symlinked(localdir)
    sys.path = oldpath
    del sys.modules['winutils']
    print('WARNING: your working copy is now dirty by changes in samplesite, sphinx and themes')
    if failures:
        raise Exception("Error: \n\tnot all symlinked files could be fixed." +
                        "\n\tYour best bet is to start again from clean.")