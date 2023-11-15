def get_user_site():
    site_dirs = []
    try:
        if not on_win:
            if exists(expanduser('~/.local/lib')):
                python_re = re.compile('python\d\.\d')
                for path in listdir(expanduser('~/.local/lib/')):
                    if python_re.match(path):
                        site_dirs.append("~/.local/lib/%s" % path)
        else:
            if 'APPDATA' not in os.environ:
                return site_dirs
            APPDATA = os.environ[str('APPDATA')]
            if exists(join(APPDATA, 'Python')):
                site_dirs = [join(APPDATA, 'Python', i) for i in
                             listdir(join(APPDATA, 'PYTHON'))]
    except (IOError, OSError) as e:
        log.debug('Error accessing user site directory.\n%r', e)
    return site_dirs