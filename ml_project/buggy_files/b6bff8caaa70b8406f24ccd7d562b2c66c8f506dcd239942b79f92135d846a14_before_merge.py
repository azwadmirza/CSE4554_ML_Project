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
        if "dev-packages" not in project.parsed_pipfile:
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
        package_names = project.dev_packages.keys()
    if packages is False and editable_packages is False and not all_dev:
        click.echo(crayons.red("No package provided!"), err=True)
        return 1
    for package_name in package_names:
        click.echo(fix_utf8("Un-installing {0}…".format(crayons.green(package_name))))
        cmd = "{0} uninstall {1} -y".format(
            escape_grouped_arguments(which_pip(allow_global=system)), package_name
        )
        if environments.is_verbose():
            click.echo("$ {0}".format(cmd))
        c = delegator.run(cmd)
        click.echo(crayons.blue(c.out))
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