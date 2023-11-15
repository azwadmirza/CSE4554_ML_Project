def do_ex(cmd, cwd='.'):
    trace('cmd', repr(cmd))
    if not isinstance(cmd, (list, tuple)):
        cmd = shlex.split(cmd)

    p = _popen_pipes(cmd, cwd)
    out, err = p.communicate()
    if out:
        trace('out', repr(out))
    if err:
        trace('err', repr(err))
    if p.returncode:
        trace('ret', p.returncode)
    return ensure_stripped_str(out), ensure_stripped_str(err), p.returncode