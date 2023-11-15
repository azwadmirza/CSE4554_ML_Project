def system_which(command, mult=False):
    """Emulates the system's which. Returns None if not found."""
    _which = "which -a" if not os.name == "nt" else "where"
    os.environ = {
        vistir.compat.fs_str(k): vistir.compat.fs_str(val)
        for k, val in os.environ.items()
    }
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
            return None if not mult else []
    except TypeError:
        from .vendor.pythonfinder import Finder
        finder = Finder()
        result = finder.which(command)
        if result:
            return result.path.as_posix()
        return
    else:
        result = c.out.strip() or c.err.strip()
    if mult:
        return result.split("\n")

    else:
        return result.split("\n")[0]