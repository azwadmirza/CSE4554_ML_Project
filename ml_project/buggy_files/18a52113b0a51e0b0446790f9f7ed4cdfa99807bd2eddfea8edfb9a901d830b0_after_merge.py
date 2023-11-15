def system_which(command, mult=False):
    """Emulates the system's which. Returns None if not found."""
    _which = "which -a" if not os.name == "nt" else "where"
    os.environ = {
        vistir.compat.fs_str(k): vistir.compat.fs_str(val)
        for k, val in os.environ.items()
    }
    result = None
    try:
        c = delegator.run("{0} {1}".format(_which, command))
        try:
            # Which Not found…
            if c.return_code == 127:
                click.echo(
                    "{}: the {} system utility is required for Pipenv to find Python installations properly."
                    "\n  Please install it.".format(
                        crayons.red("Warning", bold=True), crayons.red(_which)
                    ),
                    err=True,
                )
            assert c.return_code == 0
        except AssertionError:
            result = fallback_which(command, allow_global=True)
    except TypeError:
        if not result:
            result = fallback_which(command, allow_global=True)
    else:
        if not result:
            result = next(iter([c.out, c.err]), "").split("\n")
            result = next(iter(result)) if not mult else result
            return result
        if not result:
            result = fallback_which(command, allow_global=True)
    result = [result] if mult else result
    return result