def create_package_set_from_installed(**kwargs):
    # type: (**Any) -> Tuple[PackageSet, bool]
    """Converts a list of distributions into a PackageSet.
    """
    # Default to using all packages installed on the system
    if kwargs == {}:
        kwargs = {"local_only": False, "skip": ()}

    package_set = {}
    problems = False
    for dist in get_installed_distributions(**kwargs):
        name = canonicalize_name(dist.project_name)
        try:
            package_set[name] = PackageDetails(dist.version, dist.requires())
        except RequirementParseError as e:
            # Don't crash on broken metadata
            logging.warning("Error parsing requirements for %s: %s", name, e)
            problems = True
    return package_set, problems