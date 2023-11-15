def cluster_create(
    version,
    name="main",
    port=None,
    locale=None,
    encoding=None,
    datadir=None,
    allow_group_access=None,
    data_checksums=None,
    wal_segsize=None,
):
    """
    Adds a cluster to the Postgres server.

    .. warning:

       Only works for debian family distros so far.

    CLI Example:

    .. code-block:: bash

        salt '*' postgres.cluster_create '9.3'

        salt '*' postgres.cluster_create '9.3' 'main'

        salt '*' postgres.cluster_create '9.3' locale='fr_FR'

        salt '*' postgres.cluster_create '11' data_checksums=True wal_segsize='32'
    """

    cmd = [salt.utils.path.which("pg_createcluster")]
    if port:
        cmd += ["--port", str(port)]
    if locale:
        cmd += ["--locale", locale]
    if encoding:
        cmd += ["--encoding", encoding]
    if datadir:
        cmd += ["--datadir", datadir]
    cmd += [str(version), name]
    # initdb-specific options are passed after '--'
    if allow_group_access or data_checksums or wal_segsize:
        cmd += ["--"]
    if allow_group_access is True:
        cmd += ["--allow-group-access"]
    if data_checksums is True:
        cmd += ["--data-checksums"]
    if wal_segsize:
        cmd += ["--wal-segsize", wal_segsize]
    cmdstr = " ".join([pipes.quote(c) for c in cmd])
    ret = __salt__["cmd.run_all"](cmdstr, python_shell=False)
    if ret.get("retcode", 0) != 0:
        log.error("Error creating a Postgresql cluster %s/%s", version, name)
        return False
    return ret