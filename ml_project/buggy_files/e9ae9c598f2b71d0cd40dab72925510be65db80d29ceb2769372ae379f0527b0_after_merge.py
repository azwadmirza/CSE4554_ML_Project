def fix(force, paths, **kwargs):
    """Fix SQL files.

    PATH is the path to a sql file or directory to lint. This can be either a
    file ('path/to/file.sql'), a path ('directory/of/sql/files'), a single ('-')
    character to indicate reading from *stdin* or a dot/blank ('.'/' ') which will
    be interpreted like passing the current working directory as a path argument.
    """
    c = get_config(**kwargs)
    lnt = get_linter(c)
    verbose = c.get('verbose')

    config_string = format_config(lnt, verbose=verbose)
    if len(config_string) > 0:
        lnt.log(config_string)
    # Check that if fix is specified, that we have picked only a subset of rules
    if lnt.config.get('rule_whitelist') is None:
        lnt.log(("The fix option is only available in combination"
                 " with --rules. This is for your own safety!"))
        sys.exit(1)

    # handle stdin case. should output formatted sql to stdout and nothing else.
    if ('-',) == paths:
        stdin = sys.stdin.read()
        result = lnt.lint_string_wrapped(stdin, fname='stdin', verbosity=verbose, fix=True)
        stdout = result.paths[0].files[0].fix_string()
        click.echo(stdout, nl=False)
        sys.exit()

    # Lint the paths (not with the fix argument at this stage), outputting as we go.
    lnt.log("==== finding violations ====")
    try:
        result = lnt.lint_paths(paths, verbosity=verbose)
    except IOError:
        click.echo(colorize('The path(s) {0!r} could not be accessed. Check it/they exist(s).'.format(paths), 'red'))
        sys.exit(1)

    # NB: We filter to linting violations here, because they're
    # the only ones which can be potentially fixed.
    if result.num_violations(types=SQLLintError) > 0:
        click.echo("==== fixing violations ====")
        click.echo("{0} linting violations found".format(
            result.num_violations(types=SQLLintError)))
        if force:
            click.echo('FORCE MODE: Attempting fixes...')
            success = do_fixes(lnt, paths, types=SQLLintError)
            if not success:
                sys.exit(1)
        else:
            click.echo('Are you sure you wish to attempt to fix these? [Y/n] ', nl=False)
            c = click.getchar().lower()
            click.echo('...')
            if c == 'y':
                click.echo('Attempting fixes...')
                success = do_fixes(lnt, paths)
                if not success:
                    sys.exit(1)
            elif c == 'n':
                click.echo('Aborting...')
            else:
                click.echo('Invalid input :(')
                click.echo('Aborting...')
    else:
        click.echo("==== no linting violations found ====")
    sys.exit(0)