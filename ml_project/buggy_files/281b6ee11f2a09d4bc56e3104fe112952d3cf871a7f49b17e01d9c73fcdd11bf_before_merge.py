def pip_install(
    package_name=None, r=None, allow_global=False, ignore_hashes=False,
    no_deps=True, verbose=False, block=True, index=None, pre=False
):

    if verbose:
        click.echo(crayons.normal('Installing {0!r}'.format(package_name), bold=True), err=True)

    # Create files for hash mode.
    if (not ignore_hashes) and (r is None):
        r = tempfile.mkstemp(prefix='pipenv-', suffix='-requirement.txt')[1]
        with open(r, 'w') as f:
            f.write(package_name)

    # Install dependencies when a package is a VCS dependency.
    if get_requirement(package_name.split('--hash')[0].split('--trusted-host')[0]).vcs:
        no_deps = False

        # Don't specify a source directory when using --system.
        if not allow_global and ('PIP_SRC' not in os.environ):
            src = '--src {0}'.format(project.virtualenv_src_location)
        else:
            src = ''
    else:
        src = ''

    # Try installing for each source in project.sources.
    if index:
        sources = [{'url': index}]
    else:
        sources = project.sources

    for source in sources:
        if r:
            install_reqs = ' -r {0}'.format(r)
        elif package_name.startswith('-e '):
            install_reqs = ' -e "{0}"'.format(package_name.split('-e ')[1])
        else:
            install_reqs = ' "{0}"'.format(package_name)

        # Skip hash-checking mode, when appropriate.
        if r:
            with open(r) as f:
                if '--hash' not in f.read():
                    ignore_hashes = True
        else:
            if '--hash' not in install_reqs:
                ignore_hashes = True

        verbose_flag = '--verbose' if verbose else ''

        if not ignore_hashes:
            install_reqs += ' --require-hashes'

        no_deps = '--no-deps' if no_deps else ''
        pre = '--pre' if pre else ''

        quoted_pip = which_pip(allow_global=allow_global)
        quoted_pip = shellquote(quoted_pip)

        pip_command = '{0} install {4} {5} {6} {3} {1} {2} --exists-action w'.format(
            quoted_pip,
            install_reqs,
            ' '.join(prepare_pip_source_args([source])),
            no_deps,
            pre,
            src,
            verbose_flag
        )

        if verbose:
            click.echo('$ {0}'.format(pip_command), err=True)

        c = delegator.run(pip_command, block=block)
        if c.return_code == 0:
            break

    # Return the result of the first one that runs ok, or the last one that didn't work.
    return c