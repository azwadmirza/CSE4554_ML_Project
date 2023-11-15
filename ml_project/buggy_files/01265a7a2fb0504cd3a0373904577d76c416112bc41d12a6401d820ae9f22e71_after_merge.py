def cluster_exists(version, name="main"):
    """
    Checks if a given version and name of a cluster exists.

    CLI Example:

    .. code-block:: bash

        salt '*' postgres.cluster_exists '9.3'

        salt '*' postgres.cluster_exists '9.3' 'main'
    """
    return "{}/{}".format(version, name) in cluster_list()