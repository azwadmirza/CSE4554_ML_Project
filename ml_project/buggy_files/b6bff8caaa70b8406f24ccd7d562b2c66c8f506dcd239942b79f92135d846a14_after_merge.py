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
    editable_pkgs = [
        Requirement.from_line("-e {0}".format(p)).name for p in editable_packages if p
    ]
    package_names = [p for p in packages if p] + editable_pkgs
    installed_package_names = set([
        canonicalize_name(pkg.project_name) for pkg in project.get_installed_packages()
    ])
    # Intelligently detect if --dev should be used or not.
    if project.lockfile_exists:
        develop = set(
            [canonicalize_name(k) for k in project.lockfile_content["develop"].keys()]
        )
        default = set(
            [canonicalize_name(k) for k in project.lockfile_content["default"].keys()]
        )
    else:
        develop = set(
            [canonicalize_name(k) for k in project.dev_packages.keys()]
        )
        default = set(
            [canonicalize_name(k) for k in project.packages.keys()]
        )
    pipfile_remove = True
    # Un-install all dependencies, if --all was provided.
    if all is True:
        click.echo(
            crayons.normal(fix_utf8("Un-installing all packages from virtualenv…"), bold=True)
        )
        do_purge(allow_global=system)
        return
    # Uninstall [dev-packages], if --dev was provided.
    if all_dev:
        if "dev-packages" not in project.parsed_pipfile and not develop:
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
    if packages is False and editable_packages is False and not all_dev:
        click.echo(crayons.red("No package provided!"), err=True)
        return 1
    fix_venv_site(project.env_paths["lib"])
    # Remove known "bad packages" from the list.
    for bad_package in BAD_PACKAGES:
        if canonicalize_name(bad_package) in package_names:
            if environments.is_verbose():
                click.echo("Ignoring {0}.".format(repr(bad_package)), err=True)
            del package_names[package_names.index(
                canonicalize_name(bad_package)
            )]
    used_packages = (develop | default) & installed_package_names
    failure = False
    packages_to_remove = set()
    if all_dev:
        packages_to_remove |= develop & installed_package_names
    package_names = set([canonicalize_name(pkg_name) for pkg_name in package_names])
    packages_to_remove = package_names & used_packages
    for package_name in packages_to_remove:
        click.echo(
            crayons.white(
                fix_utf8("Uninstalling {0}…".format(repr(package_name))), bold=True
            )
        )
        # Uninstall the package.
        cmd = "{0} uninstall {1} -y".format(
                    escape_grouped_arguments(which_pip()), package_name
                )
        if environments.is_verbose():
            click.echo("$ {0}".format(cmd))
        c = delegator.run(cmd)
        click.echo(crayons.blue(c.out))
        if c.return_code != 0:
            failure = True
        else:
            if pipfile_remove:
                in_packages = project.get_package_name_in_pipfile(package_name, dev=False)
                in_dev_packages = project.get_package_name_in_pipfile(
                    package_name, dev=True
                )
                if not in_dev_packages and not in_packages:
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
                project.remove_package_from_pipfile(package_name, dev=True)
                project.remove_package_from_pipfile(package_name, dev=False)
    if lock:
        do_lock(system=system, keep_outdated=keep_outdated, pypi_mirror=pypi_mirror)
    sys.exit(int(failure))