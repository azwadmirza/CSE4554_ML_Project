def do_uninstall(
    packages=False,
    editable_packages=False,
    three=None,
    python=False,
    system=False,
    lock=False,
    all_dev=False,
    all=False,
    keep_outdated=False,
    pypi_mirror=None,
    ctx=None
):
    from .environments import PIPENV_USE_SYSTEM
    from .vendor.requirementslib.models.requirements import Requirement
    from .vendor.packaging.utils import canonicalize_name

    # Automatically use an activated virtualenv.
    if PIPENV_USE_SYSTEM:
        system = True
    # Ensure that virtualenv is available.
    # TODO: We probably shouldn't ensure a project exists if the outcome will be to just
    # install things in order to remove them... maybe tell the user to install first?
    ensure_project(three=three, python=python, pypi_mirror=pypi_mirror)
    # Un-install all dependencies, if --all was provided.
    if not any([packages, editable_packages, all_dev, all]):
        raise exceptions.MissingParameter(
            crayons.red("No package provided!"),
            ctx=ctx, param_type="parameter",
        )
    editable_pkgs = [
        Requirement.from_line("-e {0}".format(p)).name for p in editable_packages if p
    ]
    packages = packages + editable_pkgs
    package_names = [p for p in packages if p]
    package_map = {
        canonicalize_name(p): p for p in packages if p
    }
    installed_package_names = project.installed_package_names
    # Intelligently detect if --dev should be used or not.
    lockfile_packages = set()
    if project.lockfile_exists:
        project_pkg_names = project.lockfile_package_names
    else:
        project_pkg_names = project.pipfile_package_names
    pipfile_remove = True
    # Uninstall [dev-packages], if --dev was provided.
    if all_dev:
        if "dev-packages" not in project.parsed_pipfile and not project_pkg_names["dev"]:
            click.echo(
                crayons.normal(
                    "No {0} to uninstall.".format(crayons.red("[dev-packages]")),
                    bold=True,
                )
            )
            return
        click.echo(
            crayons.normal(
                fix_utf8("Un-installing {0}…".format(crayons.red("[dev-packages]"))), bold=True
            )
        )
        package_names = project_pkg_names["dev"]

    # Remove known "bad packages" from the list.
    bad_pkgs = get_canonical_names(BAD_PACKAGES)
    ignored_packages = bad_pkgs & set(list(package_map.keys()))
    for ignored_pkg in ignored_packages:
        if environments.is_verbose():
            click.echo("Ignoring {0}.".format(ignored_pkg), err=True)
        pkg_name_index = package_names.index(package_map[ignored_pkg])
        del package_names[pkg_name_index]

    used_packages = project_pkg_names["combined"] & installed_package_names
    failure = False
    packages_to_remove = set()
    if all:
        click.echo(
            crayons.normal(
                fix_utf8("Un-installing all {0} and {1}…".format(
                    crayons.red("[dev-packages]"),
                    crayons.red("[packages]"),
                )), bold=True
            )
        )
        do_purge(bare=False, allow_global=system)
        sys.exit(0)
    if all_dev:
        package_names = project_pkg_names["dev"]
    else:
        package_names = set([pkg_name for pkg_name in package_names])
    selected_pkg_map = {
        canonicalize_name(p): p for p in package_names
    }
    packages_to_remove = [
        p for normalized, p in selected_pkg_map.items()
        if normalized in (used_packages - bad_pkgs)
    ]
    pip_path = None
    for normalized, package_name in selected_pkg_map.items():
        click.echo(
            crayons.white(
                fix_utf8("Uninstalling {0}…".format(package_name)), bold=True
            )
        )
        # Uninstall the package.
        if package_name in packages_to_remove:
            with project.environment.activated():
                if pip_path is None:
                    pip_path = which_pip(allow_global=system)
                cmd = [pip_path, "uninstall", package_name, "-y"]
                c = run_command(cmd)
                click.echo(crayons.blue(c.out))
                if c.return_code != 0:
                    failure = True
        if not failure and pipfile_remove:
            in_packages = project.get_package_name_in_pipfile(package_name, dev=False)
            in_dev_packages = project.get_package_name_in_pipfile(
                package_name, dev=True
            )
            if normalized in lockfile_packages:
                click.echo("{0} {1} {2} {3}".format(
                    crayons.blue("Removing"),
                    crayons.green(package_name),
                    crayons.blue("from"),
                    crayons.white(fix_utf8("Pipfile.lock…")))
                )
                lockfile = project.get_or_create_lockfile()
                if normalized in lockfile.default:
                    del lockfile.default[normalized]
                if normalized in lockfile.develop:
                    del lockfile.develop[normalized]
                lockfile.write()
            if not (in_dev_packages or in_packages):
                if normalized in lockfile_packages:
                    continue
                click.echo(
                    "No package {0} to remove from Pipfile.".format(
                        crayons.green(package_name)
                    )
                )
                continue

            click.echo(
                fix_utf8("Removing {0} from Pipfile…".format(crayons.green(package_name)))
            )
            # Remove package from both packages and dev-packages.
            if in_dev_packages:
                project.remove_package_from_pipfile(package_name, dev=True)
            if in_packages:
                project.remove_package_from_pipfile(package_name, dev=False)
    if lock:
        do_lock(system=system, keep_outdated=keep_outdated, pypi_mirror=pypi_mirror)
    sys.exit(int(failure))