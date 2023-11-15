def create_package_set_from_installed(**kwargs):
    # type: (**Any) -> PackageSet
    """Converts a list of distributions into a PackageSet.
    """
    # Default to using all packages installed on the system
    if kwargs == {}:
        kwargs = {"local_only": False, "skip": ()}

    package_set = {}
    for dist in get_installed_distributions(**kwargs):
        name = canonicalize_name(dist.project_name)
        package_set[name] = PackageDetails(dist.version, dist.requires())
    return package_set