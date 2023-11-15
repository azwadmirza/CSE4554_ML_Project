def qt_args(namespace: argparse.Namespace) -> List[str]:
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

    if objects.backend != usertypes.Backend.QtWebEngine:
        assert objects.backend == usertypes.Backend.QtWebKit, objects.backend
        return argv

    special_prefixes = (_ENABLE_FEATURES, _DISABLE_FEATURES, _BLINK_SETTINGS)
    special_flags = [flag for flag in argv if flag.startswith(special_prefixes)]
    argv = [flag for flag in argv if not flag.startswith(special_prefixes)]
    argv += list(_qtwebengine_args(namespace, special_flags))

    return argv