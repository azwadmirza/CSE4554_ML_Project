def do_clean(
    ctx, three=None, python=None, dry_run=False, bare=False, verbose=False
):
    # Ensure that virtualenv is available.
    ensure_project(three=three, python=python, validate=False)
    ensure_lockfile()
    installed_packages = delegator.run(
        '{0} freeze'.format(which('pip'))
    ).out.strip(
    ).split(
        '\n'
    )
    installed_package_names = []
    for installed in installed_packages:
        r = get_requirement(installed)
        # Ignore editable installations.
        if not r.editable:
            installed_package_names.append(r.name.lower())
        else:
            if verbose:
                click.echo('Ignoring {0}.'.format(repr(r.name)), err=True)
    # Remove known "bad packages" from the list.
    for bad_package in BAD_PACKAGES:
        if bad_package in installed_package_names:
            if verbose:
                click.echo('Ignoring {0}.'.format(repr(bad_package)), err=True)
            del installed_package_names[
                installed_package_names.index(bad_package)
            ]
    # Intelligently detect if --dev should be used or not.
    develop = [k.lower() for k in project.lockfile_content['develop'].keys()]
    default = [k.lower() for k in project.lockfile_content['default'].keys()]
    for used_package in set(develop + default):
        if used_package in installed_package_names:
            del installed_package_names[
                installed_package_names.index(used_package)
            ]
    failure = False
    for apparent_bad_package in installed_package_names:
        if dry_run:
            click.echo(apparent_bad_package)
        else:
            click.echo(
                crayons.white(
                    'Uninstalling {0}…'.format(repr(apparent_bad_package)),
                    bold=True,
                )
            )
            # Uninstall the package.
            c = delegator.run(
                '{0} uninstall {1} -y'.format(
                    which('pip'), apparent_bad_package
                )
            )
            if c.return_code != 0:
                failure = True
    sys.exit(int(failure))