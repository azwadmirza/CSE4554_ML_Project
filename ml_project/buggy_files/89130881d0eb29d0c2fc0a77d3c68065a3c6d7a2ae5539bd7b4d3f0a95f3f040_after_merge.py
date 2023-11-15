def virtualenv_ver(venv_bin, user=None, **kwargs):
    """
    return virtualenv version if exists
    """
    # Virtualenv package
    try:
        import virtualenv

        version = getattr(virtualenv, "__version__", None)
        if not version:
            version = virtualenv.virtualenv_version
    except ImportError:
        # Unable to import?? Let's parse the version from the console
        version_cmd = [venv_bin, "--version"]
        ret = __salt__["cmd.run_all"](
            version_cmd, runas=user, python_shell=False, redirect_stderr=True, **kwargs
        )
        if ret["retcode"] > 0 or not ret["stdout"].strip():
            raise CommandExecutionError(
                "Unable to get the virtualenv version output using '{0}'. "
                "Returned data: {1}".format(version_cmd, ret)
            )
        # 20.0.0 virtualenv changed the --version output. find version number
        version = "".join(
            [x for x in ret["stdout"].strip().split() if re.search(r"^\d.\d*", x)]
        )
    virtualenv_version_info = tuple(
        [int(i) for i in re.sub(r"(rc|\+ds).*$", "", version).split(".")]
    )
    return virtualenv_version_info