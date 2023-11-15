def do_create_virtualenv(python=None, site_packages=False):
    """Creates a virtualenv."""

    click.echo(crayons.normal(u'Creating a virtualenv for this project…', bold=True), err=True)

    # The user wants the virtualenv in the project.
    if PIPENV_VENV_IN_PROJECT:
        cmd = ['virtualenv', project.virtualenv_location, '--prompt=({0})'.format(project.name)]

        # Pass site-packages flag to virtualenv, if desired...
        if site_packages:
            cmd.append('--system-site-packages')
    else:
        # Default: use pew.
        cmd = [sys.executable, '-m', 'pipenv.pew', 'new', project.virtualenv_name, '-d']

    if not python:
        python = find_a_system_python('3.6') or find_a_system_python('3') or sys.executable

    click.echo(u'{0} {1} {2}'.format(
        crayons.normal('Using', bold=True),
        crayons.red(python, bold=True),
        crayons.normal(u'to create virtualenv…', bold=True)
    ), err=True)

    cmd = cmd + ['-p', python]

    # Actually create the virtualenv.
    with spinner():
        try:
            c = delegator.run(cmd, block=False, timeout=PIPENV_TIMEOUT)
        except OSError:
            click.echo(
                '{0}: it looks like {1} is not in your {2}. '
                'We cannot continue until this is resolved.'
                ''.format(
                    crayons.red('Warning', bold=True),
                    crayons.red(cmd[0]),
                    crayons.normal('PATH', bold=True)
                ), err=True
            )
            sys.exit(1)

    click.echo(crayons.blue(c.out), err=True)

    # Enable site-packages, if desired...
    if not PIPENV_VENV_IN_PROJECT and site_packages:

        click.echo(crayons.normal(u'Making site-packages available…', bold=True), err=True)

        os.environ['VIRTUAL_ENV'] = project.virtualenv_location
        delegator.run('pipenv run pewtwo toggleglobalsitepackages')
        del os.environ['VIRTUAL_ENV']

    # Say where the virtualenv is.
    do_where(virtualenv=True, bare=False)