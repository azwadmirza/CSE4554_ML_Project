def _get_user_dirs(xdg_config_dir):
    """Returns a dict of XDG dirs read from
    ``$XDG_CONFIG_HOME/user-dirs.dirs``.

    This is used at import time for most users of :mod:`mopidy`. By rolling our
    own implementation instead of using :meth:`glib.get_user_special_dir` we
    make it possible for many extensions to run their test suites, which are
    importing parts of :mod:`mopidy`, in a virtualenv with global site-packages
    disabled, and thus no :mod:`glib` available.
    """

    dirs_file = os.path.join(xdg_config_dir, b'user-dirs.dirs')

    if not os.path.exists(dirs_file):
        return {}

    with open(dirs_file, 'rb') as fh:
        data = fh.read().decode('utf-8')

    data = '[XDG_USER_DIRS]\n' + data
    data = data.replace('$HOME', os.path.expanduser('~'))
    data = data.replace('"', '')

    config = configparser.RawConfigParser()
    config.readfp(io.StringIO(data))

    return {
        k.upper(): os.path.abspath(v)
        for k, v in config.items('XDG_USER_DIRS') if v is not None}