def do_outdated(pypi_mirror=None, pre=False, clear=False):
    # TODO: Allow --skip-lock here?
    from .vendor.requirementslib.models.requirements import Requirement
    from .vendor.requirementslib.models.utils import get_version
    from .vendor.packaging.utils import canonicalize_name
    from .vendor.vistir.compat import Mapping
    from collections import namedtuple

    packages = {}
    package_info = namedtuple("PackageInfo", ["name", "installed", "available"])

    installed_packages = project.environment.get_installed_packages()
    outdated_packages = {
        canonicalize_name(pkg.project_name): package_info
        (pkg.project_name, pkg.parsed_version, pkg.latest_version)
        for pkg in project.environment.get_outdated_packages()
    }
    reverse_deps = project.environment.reverse_dependencies()
    for result in installed_packages:
        dep = Requirement.from_line(str(result.as_requirement()))
        packages.update(dep.as_pipfile())
    updated_packages = {}
    lockfile = do_lock(clear=clear, pre=pre, write=False, pypi_mirror=pypi_mirror)
    for section in ("develop", "default"):
        for package in lockfile[section]:
            try:
                updated_packages[package] = lockfile[section][package]["version"]
            except KeyError:
                pass
    outdated = []
    skipped = []
    for package in packages:
        norm_name = pep423_name(package)
        if norm_name in updated_packages:
            if updated_packages[norm_name] != packages[package]:
                outdated.append(
                    package_info(package, updated_packages[norm_name], packages[package])
                )
            elif canonicalize_name(package) in outdated_packages:
                skipped.append(outdated_packages[canonicalize_name(package)])
    for package, old_version, new_version in skipped:
        name_in_pipfile = project.get_package_name_in_pipfile(package)
        pipfile_version_text = ""
        required = ""
        version = None
        if name_in_pipfile:
            version = get_version(project.packages[name_in_pipfile])
            reverse_deps = reverse_deps.get(name_in_pipfile)
            if isinstance(reverse_deps, Mapping) and "required" in reverse_deps:
                required = " {0} required".format(reverse_deps["required"])
            if version:
                pipfile_version_text = " ({0} set in Pipfile)".format(version)
            else:
                pipfile_version_text = " (Unpinned in Pipfile)"
        click.echo(
            crayons.yellow(
                "Skipped Update of Package {0!s}: {1!s} installed,{2!s}{3!s}, "
                "{4!s} available.".format(
                    package, old_version, required, pipfile_version_text, new_version
                )
            ), err=True
        )
    if not outdated:
        click.echo(crayons.green("All packages are up to date!", bold=True))
        sys.exit(0)
    for package, new_version, old_version in outdated:
        click.echo(
            "Package {0!r} out-of-date: {1!r} installed, {2!r} available.".format(
                package, old_version, new_version
            )
        )
    sys.exit(bool(outdated))