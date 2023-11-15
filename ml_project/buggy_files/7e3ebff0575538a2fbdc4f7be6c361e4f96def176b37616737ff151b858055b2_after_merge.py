def actually_resolve_reps(deps, index_lookup, markers_lookup, project, sources, verbose, clear, pre):

    class PipCommand(pip.basecommand.Command):
        """Needed for pip-tools."""
        name = 'PipCommand'

    constraints = []

    for dep in deps:
        t = tempfile.mkstemp(prefix='pipenv-', suffix='-requirement.txt')[1]
        with open(t, 'w') as f:
            f.write(dep)

        if dep.startswith('-e '):
            constraint = pip.req.InstallRequirement.from_editable(dep[len('-e '):])
        else:
            constraint = [c for c in pip.req.parse_requirements(t, session=pip._vendor.requests)][0]
            # extra_constraints = []

        if ' -i ' in dep:
            index_lookup[constraint.name] = project.get_source(url=dep.split(' -i ')[1]).get('name')

        if constraint.markers:
            markers_lookup[constraint.name] = str(constraint.markers).replace('"', "'")

        constraints.append(constraint)

    pip_command = get_pip_command()

    pip_args = []

    if sources:
        pip_args = prepare_pip_source_args(sources, pip_args)

    if verbose:
        print('Using pip: {0}'.format(' '.join(pip_args)))

    pip_options, _ = pip_command.parse_args(pip_args)

    session = pip_command._build_session(pip_options)
    pypi = PyPIRepository(pip_options=pip_options, session=session)

    if verbose:
        logging.log.verbose = True


    resolved_tree = set()

    resolver = Resolver(constraints=constraints, repository=pypi, clear_caches=clear, prereleases=pre)
    # pre-resolve instead of iterating to avoid asking pypi for hashes of editable packages
    try:
        resolved_tree.update(resolver.resolve(max_rounds=PIPENV_MAX_ROUNDS))
    except (NoCandidateFound, DistributionNotFound, HTTPError) as e:
        click.echo(
            '{0}: Your dependencies could not be resolved. You likely have a mismatch in your sub-dependencies.\n  '
            'You can use {1} to bypass this mechanism, then run {2} to inspect the situation.'
            ''.format(
                crayons.red('Warning', bold=True),
                crayons.red('$ pipenv install --skip-lock'),
                crayons.red('$ pipenv graph')
            ),
            err=True)

        click.echo(crayons.blue(str(e)))

        if 'no version found at all' in str(e):
            click.echo(crayons.blue('Please check your version specifier and version number. See PEP440 for more information.'))

        raise RuntimeError

    return resolved_tree, resolver