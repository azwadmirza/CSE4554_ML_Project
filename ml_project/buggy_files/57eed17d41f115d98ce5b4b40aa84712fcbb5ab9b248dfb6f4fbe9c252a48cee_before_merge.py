def cluster_remove(version, name="main", stop=False):
    """
    Remove a cluster on a Postgres server. By default it doesn't try
    to stop the cluster.

    CLI Example:

    .. code-block:: bash

        salt '*' postgres.cluster_remove '9.3'

        salt '*' postgres.cluster_remove '9.3' 'main'

        salt '*' postgres.cluster_remove '9.3' 'main' stop=True

    """
    cmd = [salt.utils.path.which("pg_dropcluster")]
    if stop:
        cmd += ["--stop"]
    cmd += [version, name]
    cmdstr = " ".join([pipes.quote(c) for c in cmd])
    ret = __salt__["cmd.run_all"](cmdstr, python_shell=False)
    # FIXME - return Boolean ?
    if ret.get("retcode", 0) != 0:
        log.error("Error removing a Postgresql cluster %s/%s", version, name)
    else:
        ret["changes"] = ("Successfully removed" " cluster {0}/{1}").format(
            version, name
        )
    return ret