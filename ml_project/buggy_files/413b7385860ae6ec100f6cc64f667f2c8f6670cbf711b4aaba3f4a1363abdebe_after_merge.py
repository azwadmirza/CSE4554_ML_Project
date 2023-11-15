def shell(three=None, python=False, compat=False, shell_args=None, anyway=False):

    # Prevent user from activating nested environments.
    if 'PIPENV_ACTIVE' in os.environ:
        # If PIPENV_ACTIVE is set, VIRTUAL_ENV should always be set too.
        venv_name = os.environ.get('VIRTUAL_ENV', 'UNKNOWN_VIRTUAL_ENVIRONMENT')

        if not anyway:
            click.echo('{0} {1} {2}\nNo action taken to avoid nested environments.'.format(
                crayons.white('Shell for'),
                crayons.green(venv_name, bold=True),
                crayons.white('already activated.', bold=True)
            ), err=True)

            sys.exit(1)

    # Ensure that virtualenv is available.
    ensure_project(three=three, python=python, validate=False)

    # Load .env file.
    load_dot_env()

    do_shell(three=three, python=python, compat=compat, shell_args=shell_args)