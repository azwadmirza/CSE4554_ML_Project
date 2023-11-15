def _parse_pg_lscluster(output):
    """
    Helper function to parse the output of pg_lscluster
    """
    cluster_dict = {}
    for line in output.splitlines():
        version, name, port, status, user, datadir, log = line.split()
        cluster_dict["{0}/{1}".format(version, name)] = {
            "port": int(port),
            "status": status,
            "user": user,
            "datadir": datadir,
            "log": log,
        }
    return cluster_dict