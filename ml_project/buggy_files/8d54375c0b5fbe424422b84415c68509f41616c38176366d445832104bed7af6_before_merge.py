def _info(ns):
    data = [
        ('xonsh', XONSH_VERSION),
        ('Python', '{}.{}.{}'.format(*PYTHON_VERSION_INFO)),
        ('PLY', ply.__version__),
        ('have readline', is_readline_available()),
        ('prompt toolkit', ptk_version() or None),
        ('shell type', builtins.__xonsh_env__.get('SHELL_TYPE')),
        ('pygments', pygments_version()),
        ('on posix', ON_POSIX),
        ('on linux', ON_LINUX)]
    if ON_LINUX:
        data.append(('distro', linux_distro()))
    data.extend([
        ('on darwin', ON_DARWIN),
        ('on windows', ON_WINDOWS),
        ('on cygwin', ON_CYGWIN),
        ('is superuser', is_superuser()),
        ('default encoding', DEFAULT_ENCODING),
        ])
    formatter = _xonfig_format_json if ns.json else __xonfig_format_human
    s = formatter(data)
    return s