def version(name, check_remote=False, source=None, pre_versions=False):
    '''
    Instructs Chocolatey to check an installed package version, and optionally
    compare it to one available from a remote feed.

    Args:

        name (str):
            The name of the package to check. Required.

        check_remote (bool):
            Get the version number of the latest package from the remote feed.
            Default is False.

        source (str):
            Chocolatey repository (directory, share or remote URL feed) the
            package comes from. Defaults to the official Chocolatey feed.
            Default is None.

        pre_versions (bool):
            Include pre-release packages in comparison. Default is False.

    Returns:
        dict: A dictionary of currently installed software and versions

    CLI Example:

    .. code-block:: bash

        salt "*" chocolatey.version <package name>
        salt "*" chocolatey.version <package name> check_remote=True
    '''
    installed = list_(narrow=name, local_only=True)
    installed = {k.lower(): v for k, v in installed.items()}

    packages = {}
    lower_name = name.lower()
    for pkg in installed:
        if lower_name in pkg.lower():
            packages[pkg] = installed[pkg]

    if check_remote:
        available = list_(narrow=name, pre_versions=pre_versions, source=source)
        available = {k.lower(): v for k, v in available.items()}

        for pkg in packages:
            packages[pkg] = {'installed': installed[pkg],
                             'available': available[pkg]}

    return packages