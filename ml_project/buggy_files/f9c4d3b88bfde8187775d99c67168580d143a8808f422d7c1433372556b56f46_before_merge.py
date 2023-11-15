def do_install_dependencies(
    dev=False,
    only=False,
    bare=False,
    requirements=False,
    allow_global=False,
    ignore_hashes=False,
    skip_lock=False,
    verbose=False,
    concurrent=True,
    requirements_dir=None,
):
    """"Executes the install functionality.

    If requirements is True, simply spits out a requirements format to stdout.
    """

    def cleanup_procs(procs, concurrent):
        for c in procs:
            if concurrent:
                c.block()
            if 'Ignoring' in c.out:
                click.echo(crayons.yellow(c.out.strip()))
            if verbose:
                click.echo(crayons.blue(c.out or c.err))
            # The Installation failed...
            if c.return_code != 0:
                # Save the Failed Dependency for later.
                failed_deps_list.append((c.dep, c.ignore_hash))
                # Alert the user.
                click.echo(
                    '{0} {1}! Will try again.'.format(
                        crayons.red('An error occurred while installing'),
                        crayons.green(c.dep.split('--hash')[0].strip()),
                    )
                )

    if requirements:
        bare = True
    blocking = (not concurrent)
    # Load the lockfile if it exists, or if only is being used (e.g. lock is being used).
    if skip_lock or only or not project.lockfile_exists:
        if not bare:
            click.echo(
                crayons.normal(
                    u'Installing dependencies from Pipfile…', bold=True
                )
            )
            lockfile = split_file(project._lockfile)
    else:
        with open(project.lockfile_location) as f:
            lockfile = split_file(simplejson.load(f))
        if not bare:
            click.echo(
                crayons.normal(
                    u'Installing dependencies from Pipfile.lock ({0})…'.format(
                        lockfile['_meta'].get('hash', {}).get('sha256')[-6:]
                    ),
                    bold=True,
                )
            )
    # Allow pip to resolve dependencies when in skip-lock mode.
    no_deps = (not skip_lock)
    deps_list, dev_deps_list = merge_deps(
        lockfile,
        project,
        dev=dev,
        requirements=requirements,
        ignore_hashes=ignore_hashes,
        blocking=blocking,
        only=only,
    )
    failed_deps_list = []
    if requirements:
        # Comment out packages that shouldn't be included in
        # requirements.txt, for pip9.
        # Additional package selectors, specific to pip's --hash checking mode.
        for l in (deps_list, dev_deps_list):
            for i, dep in enumerate(l):
                l[i] = list(l[i])
                if '--hash' in l[i][0]:
                    l[i][0] = (l[i][0].split('--hash')[0].strip())
        index_args = prepare_pip_source_args(project.sources)
        index_args = ' '.join(index_args).replace(' -', '\n-')
        # Output only default dependencies
        click.echo(index_args)
        if not dev:
            click.echo('\n'.join(d[0] for d in sorted(deps_list)))
            sys.exit(0)
        # Output only dev dependencies
        if dev:
            click.echo('\n'.join(d[0] for d in sorted(dev_deps_list)))
            sys.exit(0)
    procs = []
    deps_list_bar = progress.bar(
        deps_list, label=INSTALL_LABEL if os.name != 'nt' else ''
    )
    for dep, ignore_hash, block in deps_list_bar:
        if len(procs) < PIPENV_MAX_SUBPROCESS:
            # Use a specific index, if specified.
            dep, index = split_argument(dep, short='i', long_='index')
            dep, extra_index = split_argument(dep, long_='extra-index-url')
            # Install the module.
            c = pip_install(
                dep,
                ignore_hashes=ignore_hash,
                allow_global=allow_global,
                no_deps=no_deps,
                verbose=verbose,
                block=block,
                index=index,
                requirements_dir=requirements_dir,
                extra_indexes=extra_index,
            )
            c.dep = dep
            c.ignore_hash = ignore_hash
            procs.append(c)
        if len(procs) >= PIPENV_MAX_SUBPROCESS or len(procs) == len(deps_list):
            cleanup_procs(procs, concurrent)
            procs = []
    cleanup_procs(procs, concurrent)
    # Iterate over the hopefully-poorly-packaged dependencies...
    if failed_deps_list:
        click.echo(
            crayons.normal(
                u'Installing initially–failed dependencies…', bold=True
            )
        )
        for dep, ignore_hash in progress.bar(
            failed_deps_list, label=INSTALL_LABEL2
        ):
            # Use a specific index, if specified.
            dep, index = split_argument(dep, short='i', long_='index')
            dep, extra_index = split_argument(dep, long_='extra-index-url')
            # Install the module.
            c = pip_install(
                dep,
                ignore_hashes=ignore_hash,
                allow_global=allow_global,
                no_deps=no_deps,
                verbose=verbose,
                index=index,
                requirements_dir=requirements_dir,
                extra_indexes=extra_index,
            )
            # The Installation failed...
            if c.return_code != 0:
                # We echo both c.out and c.err because pip returns error details on out.
                click.echo(crayons.blue(format_pip_output(c.out)))
                click.echo(crayons.blue(format_pip_error(c.err)), err=True)
                # Return the subprocess' return code.
                sys.exit(c.return_code)
            else:
                click.echo(
                    '{0} {1}{2}'.format(
                        crayons.green('Success installing'),
                        crayons.green(dep.split('--hash')[0].strip()),
                        crayons.green('!'),
                    )
                )