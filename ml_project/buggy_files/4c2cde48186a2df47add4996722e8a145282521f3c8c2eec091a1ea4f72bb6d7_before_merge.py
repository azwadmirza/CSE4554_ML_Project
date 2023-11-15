def do_outdated(pypi_mirror=None):
    from .vendor.requirementslib.models.requirements import Requirement

    packages = {}
    results = delegator.run("{0} freeze".format(which("pip"))).out.strip().split("\n")
    results = filter(bool, results)
    for result in results:
        dep = Requirement.from_line(result)
        packages.update(dep.as_pipfile())
    updated_packages = {}
    lockfile = do_lock(write=False, pypi_mirror=pypi_mirror)
    for section in ("develop", "default"):
        for package in lockfile[section]:
            try:
                updated_packages[package] = lockfile[section][package]["version"]
            except KeyError:
                pass
    outdated = []
    for package in packages:
        norm_name = pep423_name(package)
        if norm_name in updated_packages:
            if updated_packages[norm_name] != packages[package]:
                outdated.append(
                    (package, updated_packages[norm_name], packages[package])
                )
    for package, new_version, old_version in outdated:
        click.echo(
            "Package {0!r} out-of-date: {1!r} installed, {2!r} available.".format(
                package, old_version, new_version
            )
        )
    sys.exit(bool(outdated))