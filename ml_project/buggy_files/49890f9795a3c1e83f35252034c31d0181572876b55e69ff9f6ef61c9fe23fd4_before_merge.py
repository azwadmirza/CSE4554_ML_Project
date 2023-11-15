def venv_resolve_deps(
    deps,
    which,
    project,
    pre=False,
    clear=False,
    allow_global=False,
    pypi_mirror=None,
):
    from .vendor.vistir.misc import fs_str
    from .vendor.vistir.compat import Path, to_native_string, JSONDecodeError
    from .vendor.vistir.path import create_tracked_tempdir
    from .cmdparse import Script
    from .core import spinner
    from .vendor.pexpect.exceptions import EOF, TIMEOUT
    from .vendor import delegator
    from . import resolver
    from ._compat import decode_output
    import json

    if not deps:
        return []

    req_dir = create_tracked_tempdir(prefix="pipenv", suffix="requirements")
    cmd = [
        which("python", allow_global=allow_global),
        Path(resolver.__file__.rstrip("co")).as_posix()
    ]
    if pre:
        cmd.append("--pre")
    if clear:
        cmd.append("--clear")
    if allow_global:
        cmd.append("--system")
    with temp_environ():
        os.environ = {fs_str(k): fs_str(val) for k, val in os.environ.items()}
        os.environ["PIPENV_PACKAGES"] = str("\n".join(deps))
        if pypi_mirror:
            os.environ["PIPENV_PYPI_MIRROR"] = str(pypi_mirror)
        os.environ["PIPENV_VERBOSITY"] = str(environments.PIPENV_VERBOSITY)
        os.environ["PIPENV_REQ_DIR"] = fs_str(req_dir)
        os.environ["PIP_NO_INPUT"] = fs_str("1")
        out = to_native_string("")
        EOF.__module__ = "pexpect.exceptions"
        with spinner(text=fs_str("Locking..."), spinner_name=environments.PIPENV_SPINNER,
                nospin=environments.PIPENV_NOSPIN) as sp:
            c = delegator.run(Script.parse(cmd).cmdify(), block=False, env=os.environ.copy())
            _out = decode_output("")
            result = None
            while True:
                try:
                    result = c.expect(u"\n", timeout=-1)
                except (EOF, TIMEOUT):
                    pass
                if result is None:
                    break
                _out = c.subprocess.before
                if _out is not None:
                    _out = decode_output("{0}".format(_out))
                    out += _out
                    sp.text = to_native_string("{0}".format(_out[:100]))
                if environments.is_verbose():
                    if _out is not None:
                        sp._hide_cursor()
                        sp.write(_out.rstrip())
                        sp._show_cursor()
            c.block()
            if c.return_code != 0:
                sp.red.fail(environments.PIPENV_SPINNER_FAIL_TEXT.format(
                    "Locking Failed!"
                ))
                click_echo(c.out.strip(), err=True)
                click_echo(c.err.strip(), err=True)
                sys.exit(c.return_code)
            else:
                sp.green.ok(environments.PIPENV_SPINNER_OK_TEXT.format("Success!"))
    if environments.is_verbose():
        click_echo(c.out.split("RESULTS:")[0], err=True)
    try:
        return json.loads(c.out.split("RESULTS:")[1].strip())

    except (IndexError, JSONDecodeError):
        click_echo(c.out.strip(), err=True)
        click_echo(c.err.strip(), err=True)
        raise RuntimeError("There was a problem with locking.")