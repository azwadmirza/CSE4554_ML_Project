def cli(ctx, where=False, venv=False, rm=False, bare=False, three=False, python=False, help=False):

    if ctx.invoked_subcommand is None:
        # --where was passed...
        if where:
            do_where(bare=bare)
            sys.exit(0)

        if not project.pipfile_exists:
            click.echo(crayons.red('No Pipfile found.'), err=True)
            sys.exit(1)

        # --venv was passed...
        elif venv:

            with spinner():
                loc = project.virtualenv_location

            # There is no virtualenv yet.
            if not project.virtualenv_exists:
                click.echo(crayons.red('No virtualenv has been created for this project yet!'), err=True)
                sys.exit(1)
            else:
                click.echo(project.virtualenv_location)
                sys.exit(0)

        # --rm was passed...
        elif rm:

            with spinner():
                loc = project.virtualenv_location

            if project.virtualenv_exists:
                click.echo(crayons.yellow('{0} ({1})...'.format(crayons.yellow('Removing virtualenv'), crayons.green(loc))))
                with spinner():
                    # Remove the virtualenv.
                    shutil.rmtree(project.virtualenv_location)
                sys.exit(0)
            else:
                click.echo(crayons.red('No virtualenv has been created for this project yet!'), err=True)
                sys.exit(1)

        # --two / --three was passed...
        if python or three is not None:
            ensure_project(three=three, python=python)

        else:
            # Display help to user, if no commands were passed.
            click.echo(format_help(ctx.get_help()))