def do_clean(ctx, three=None, python=None, dry_run=False, bare=False, pypi_mirror=None):
    # Ensure that virtualenv is available.
    from packaging.utils import canonicalize_name
    ensure_project(three=three, python=python, validate=False, pypi_mirror=pypi_mirror)
    ensure_lockfile(pypi_mirror=pypi_mirror)
    # Make sure that the virtualenv's site packages are configured correctly
    # otherwise we may end up removing from the global site packages directory
    fix_venv_site(project.env_paths["lib"])
    installed_package_names = [
        canonicalize_name(pkg.project_name) for pkg in project.get_installed_packages()
    ]
    # Remove known "bad packages" from the list.
    for bad_package in BAD_PACKAGES:
        if canonicalize_name(bad_package) in installed_package_names:
            if environments.is_verbose():
                click.echo("Ignoring {0}.".format(repr(bad_package)), err=True)
            del installed_package_names[installed_package_names.index(
                canonicalize_name(bad_package)
            )]
    # Intelligently detect if --dev should be used or not.
    develop = [canonicalize_name(k) for k in project.lockfile_content["develop"].keys()]
    default = [canonicalize_name(k) for k in project.lockfile_content["default"].keys()]
    for used_package in set(develop + default):
        if used_package in installed_package_names:
            del installed_package_names[installed_package_names.index(
                canonicalize_name(used_package)
            )]
    failure = False
    for apparent_bad_package in installed_package_names:
        if dry_run and not bare:
            click.echo(apparent_bad_package)
        else:
            if not bare:
                click.echo(
                    crayons.white(
                        fix_utf8("Uninstalling {0}…".format(repr(apparent_bad_package))), bold=True
                    )
                )
            # Uninstall the package.
            c = delegator.run(
                "{0} uninstall {1} -y".format(which_pip(), apparent_bad_package)
            )
            if c.return_code != 0:
                failure = True
    sys.exit(int(failure))