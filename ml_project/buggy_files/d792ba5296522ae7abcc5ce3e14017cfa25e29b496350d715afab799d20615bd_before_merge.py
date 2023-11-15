def do_clean(
    ctx, three=None, python=None, dry_run=False, bare=False, pypi_mirror=None,
    system=False
):
    # Ensure that virtualenv is available.
    from packaging.utils import canonicalize_name
    ensure_project(three=three, python=python, validate=False, pypi_mirror=pypi_mirror)
    ensure_lockfile(pypi_mirror=pypi_mirror)
    # Make sure that the virtualenv's site packages are configured correctly
    # otherwise we may end up removing from the global site packages directory
    installed_package_names = project.installed_package_names.copy()
    # Remove known "bad packages" from the list.
    for bad_package in BAD_PACKAGES:
        if canonicalize_name(bad_package) in installed_package_names:
            if environments.is_verbose():
                click.echo("Ignoring {0}.".format(bad_package), err=True)
            installed_package_names.remove(canonicalize_name(bad_package))
    # Intelligently detect if --dev should be used or not.
    locked_packages = {
        canonicalize_name(pkg) for pkg in project.lockfile_package_names["combined"]
    }
    for used_package in locked_packages:
        if used_package in installed_package_names:
            installed_package_names.remove(used_package)
    failure = False
    cmd = [which_pip(allow_global=system), "uninstall", "-y", "-qq"]
    for apparent_bad_package in installed_package_names:
        if dry_run and not bare:
            click.echo(apparent_bad_package)
        else:
            if not bare:
                click.echo(
                    crayons.white(
                        fix_utf8("Uninstalling {0}…".format(apparent_bad_package)), bold=True
                    )
                )
            # Uninstall the package.
            cmd_str = Script.parse(cmd + [apparent_bad_package]).cmdify()
            c = delegator.run(cmd_str, block=True)
            if c.return_code != 0:
                failure = True
    sys.exit(int(failure))