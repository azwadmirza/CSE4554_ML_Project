def sync(to_install, to_uninstall, verbose=False, dry_run=False, pip_flags=None, install_flags=None):
    """
    Install and uninstalls the given sets of modules.
    """
    if not to_uninstall and not to_install:
        click.echo("Everything up-to-date")

    if pip_flags is None:
        pip_flags = []

    if not verbose:
        pip_flags += ['-q']

    if os.environ.get('VIRTUAL_ENV'):
        # find pip via PATH
        pip = 'pip'
    else:
        # find pip in same directory as pip-sync entry-point script
        pip = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'pip')

    if to_uninstall:
        if dry_run:
            click.echo("Would uninstall:")
            for pkg in to_uninstall:
                click.echo("  {}".format(pkg))
        else:
            check_call([pip, 'uninstall', '-y'] + pip_flags + sorted(to_uninstall))

    if to_install:
        if install_flags is None:
            install_flags = []
        if dry_run:
            click.echo("Would install:")
            for ireq in to_install:
                click.echo("  {}".format(format_requirement(ireq)))
        else:
            package_args = []
            for ireq in sorted(to_install):
                if ireq.editable:
                    package_args.extend(['-e', str(ireq.link or ireq.req)])
                else:
                    package_args.append(str(ireq.req))
            check_call([pip, 'install'] + pip_flags + install_flags + package_args)
    return 0