def qt_args(namespace):
    """Get the Qt QApplication arguments based on an argparse namespace.

    Args:
        namespace: The argparse namespace.

    Return:
        The argv list to be passed to Qt.
    """
    argv = [sys.argv[0]]

    if namespace.qt_flag is not None:
        argv += ['--' + flag[0] for flag in namespace.qt_flag]

    if namespace.qt_arg is not None:
        for name, value in namespace.qt_arg:
            argv += ['--' + name, value]

    argv += ['--' + arg for arg in config.val.qt.args]

    if (objects.backend == usertypes.Backend.QtWebEngine and
            not qtutils.version_check('5.11', compiled=False)):
        # WORKAROUND equivalent to
        # https://codereview.qt-project.org/#/c/217932/
        # Needed for Qt < 5.9.5 and < 5.10.1
        argv.append('--disable-shared-workers')

    return argv