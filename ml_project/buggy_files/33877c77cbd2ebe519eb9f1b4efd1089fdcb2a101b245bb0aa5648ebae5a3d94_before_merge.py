def do_ex(cmd, cwd='.'):
    trace('cmd', repr(cmd))
    if not isinstance(cmd, (list, tuple)):
        cmd = shlex.split(cmd)

    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(cwd),
        env=_always_strings(dict(
            os.environ,
            # try to disable i18n
            LC_ALL='C',
            LANGUAGE='',
            HGPLAIN='1',
        ))
    )

    out, err = p.communicate()
    if out:
        trace('out', repr(out))
    if err:
        trace('err', repr(err))
    if p.returncode:
        trace('ret', p.returncode)
    return ensure_stripped_str(out), ensure_stripped_str(err), p.returncode