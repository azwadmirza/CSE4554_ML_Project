def bin_pkg_info(path, saltenv="base"):
    """
    .. versionadded:: 2015.8.0

    Parses RPM metadata and returns a dictionary of information about the
    package (name, version, etc.).

    path
        Path to the file. Can either be an absolute path to a file on the
        minion, or a salt fileserver URL (e.g. ``salt://path/to/file.rpm``).
        If a salt fileserver URL is passed, the file will be cached to the
        minion so that it can be examined.

    saltenv : base
        Salt fileserver envrionment from which to retrieve the package. Ignored
        if ``path`` is a local file path on the minion.

    CLI Example:

    .. code-block:: bash

        salt '*' lowpkg.bin_pkg_info /root/foo-1.2.3-1ubuntu1_all.deb
        salt '*' lowpkg.bin_pkg_info salt://foo-1.2.3-1ubuntu1_all.deb
    """
    # If the path is a valid protocol, pull it down using cp.cache_file
    if __salt__["config.valid_fileproto"](path):
        newpath = __salt__["cp.cache_file"](path, saltenv)
        if not newpath:
            raise CommandExecutionError(
                "Unable to retrieve {0} from saltenv '{1}'".format(path, saltenv)
            )
        path = newpath
    else:
        if not os.path.exists(path):
            raise CommandExecutionError("{0} does not exist on minion".format(path))
        elif not os.path.isabs(path):
            raise SaltInvocationError("{0} does not exist on minion".format(path))

    cmd = ["dpkg", "-I", path]
    result = __salt__["cmd.run_all"](cmd, output_loglevel="trace")
    if result["retcode"] != 0:
        msg = "Unable to get info for " + path
        if result["stderr"]:
            msg += ": " + result["stderr"]
        raise CommandExecutionError(msg)

    ret = {}
    for line in result["stdout"].splitlines():
        line = line.strip()
        if re.match(r"^Package[ ]*:", line):
            ret["name"] = line.split()[-1]
        elif re.match(r"^Version[ ]*:", line):
            ret["version"] = line.split()[-1]
        elif re.match(r"^Architecture[ ]*:", line):
            ret["arch"] = line.split()[-1]

    missing = [x for x in ("name", "version", "arch") if x not in ret]
    if missing:
        raise CommandExecutionError(
            "Unable to get {0} for {1}".format(", ".join(missing), path)
        )

    if __grains__.get("cpuarch", "") == "x86_64":
        osarch = __grains__.get("osarch", "")
        arch = ret["arch"]
        if arch != "all" and osarch == "amd64" and osarch != arch:
            ret["name"] += ":{0}".format(arch)

    return ret