def do_create_virtualenv(three=None, python=None):
    """Creates a virtualenv."""
    click.echo(crayons.yellow('Creating a virtualenv for this project...'), err=True)

    # The user wants the virtualenv in the project.
    if PIPENV_VENV_IN_PROJECT:
        cmd = ['virtualenv', project.virtualenv_location, '--prompt=({0})'.format(project.name)]
    else:
        # Default: use pew.
        cmd = ['pew', 'new', project.virtualenv_name, '-d']

    # Pass a Python version to virtualenv, if needed.
    if python:
        click.echo('{0} {1} {2}'.format(crayons.yellow('Using'), crayons.red(python), crayons.yellow('to create virtualenv...')))
    else:
        if os.name == 'nt':
            click.echo('{0} If you are running on Windows, you should use the {1} option instead.'.format(crayons.red('Warning!'), crayons.green('--python')))
        if three is False:
            python = 'python2'
        elif three is True:
            python = 'python3'
    if python:
        cmd = cmd + ['-p', python]

    # Actually create the virtualenv.
    with spinner():
        c = delegator.run(cmd, block=False, timeout=PIPENV_TIMEOUT)
    click.echo(crayons.blue(c.out), err=True)

    # Say where the virtualenv is.
    do_where(virtualenv=True, bare=False)