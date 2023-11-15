def which_pip(allow_global=False):
    """Returns the location of virtualenv-installed pip."""

    location = None
    if "VIRTUAL_ENV" in os.environ:
        location = os.environ["VIRTUAL_ENV"]
    if allow_global:
        if location:
            pip = which("pip", location=location)
            if pip:
                return pip

        for p in ("pip", "pip3", "pip2"):
            where = system_which(p)
            if where:
                return where

    pip = which("pip")
    if not pip:
        pip = fallback_which("pip", allow_global=allow_global, location=location)
    return pip