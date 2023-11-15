def which_pip(allow_global=False):
    """Returns the location of virtualenv-installed pip."""
    if allow_global:
        if "VIRTUAL_ENV" in os.environ:
            return which("pip", location=os.environ["VIRTUAL_ENV"])

        for p in ("pip", "pip3", "pip2"):
            where = system_which(p)
            if where:
                return where

    return which("pip")