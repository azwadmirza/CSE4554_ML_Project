def do_install(
    package_name=False,
    more_packages=False,
    dev=False,
    three=False,
    python=False,
    system=False,
    lock=True,
    ignore_pipfile=False,
    skip_lock=False,
    verbose=False,
    requirements=False,
    sequential=False,
    pre=False,
    code=False,
    deploy=False,
    keep_outdated=False,
    selective_upgrade=False,
):
    import pip9

    requirements_directory = TemporaryDirectory(
        suffix='-requirements', prefix='pipenv-'
    )
    if selective_upgrade:
        keep_outdated = True
    more_packages = more_packages or []
    # Don't search for requirements.txt files if the user provides one
    skip_requirements = True if requirements else False
    concurrent = (not sequential)
    # Ensure that virtualenv is available.
    ensure_project(
        three=three,
        python=python,
        system=system,
        warn=True,
        deploy=deploy,
        skip_requirements=skip_requirements,
    )
    # Load the --pre settings from the Pipfile.
    if not pre:
        pre = project.settings.get('allow_prereleases')
    if not keep_outdated:
        keep_outdated = project.settings.get('keep_outdated')
    remote = requirements and is_valid_url(requirements)
    # Warn and exit if --system is used without a pipfile.
    if system and package_name and not PIPENV_VIRTUALENV:
        click.echo(
            '{0}: --system is intended to be used for Pipfile installation, '
            'not installation of specific packages. Aborting.'.format(
                crayons.red('Warning', bold=True)
            ),
            err=True,
        )
        click.echo('See also: --deploy flag.', err=True)
        requirements_directory.cleanup()
        sys.exit(1)
    # Automatically use an activated virtualenv.
    if PIPENV_USE_SYSTEM:
        system = True
    # Check if the file is remote or not
    if remote:
        fd, temp_reqs = tempfile.mkstemp(
            prefix='pipenv-',
            suffix='-requirement.txt',
            dir=requirements_directory.name,
        )
        requirements_url = requirements
        # Download requirements file
        click.echo(
            crayons.normal(
                u'Remote requirements file provided! Downloading…', bold=True
            ),
            err=True,
        )
        try:
            download_file(requirements, temp_reqs)
        except IOError:
            click.echo(
                crayons.red(
                    u'Unable to find requirements file at {0}.'.format(
                        crayons.normal(requirements)
                    )
                ),
                err=True,
            )
            requirements_directory.cleanup()
            sys.exit(1)
        # Replace the url with the temporary requirements file
        requirements = temp_reqs
        remote = True
    if requirements:
        error, traceback = None, None
        click.echo(
            crayons.normal(
                u'Requirements file provided! Importing into Pipfile…',
                bold=True,
            ),
            err=True,
        )
        try:
            import_requirements(r=project.path_to(requirements), dev=dev)
        except (UnicodeDecodeError, pip9.exceptions.PipError) as e:
            # Don't print the temp file path if remote since it will be deleted.
            req_path = requirements_url if remote else project.path_to(
                requirements
            )
            error = (
                u'Unexpected syntax in {0}. Are you sure this is a '
                'requirements.txt style file?'.format(req_path)
            )
            traceback = e
        except AssertionError as e:
            error = (
                u'Requirements file doesn\'t appear to exist. Please ensure the file exists in your '
                'project directory or you provided the correct path.'
            )
            traceback = e
        finally:
            # If requirements file was provided by remote url delete the temporary file
            if remote:
                os.close(fd)  # Close for windows to allow file cleanup.
                os.remove(project.path_to(temp_reqs))
            if error and traceback:
                click.echo(crayons.red(error))
                click.echo(crayons.blue(str(traceback)), err=True)
                requirements_directory.cleanup()
                sys.exit(1)
    if code:
        click.echo(
            crayons.normal(
                u'Discovering imports from local codebase…', bold=True
            )
        )
        for req in import_from_code(code):
            click.echo('  Found {0}!'.format(crayons.green(req)))
            project.add_package_to_pipfile(req)
    # Capture -e argument and assign it to following package_name.
    more_packages = list(more_packages)
    if package_name == '-e':
        package_name = ' '.join([package_name, more_packages.pop(0)])
    # capture indexes and extra indexes
    line = [package_name] + more_packages
    index_indicators = ['-i', '--index', '--extra-index-url']
    index, extra_indexes = None, None
    if more_packages and any(more_packages[0].startswith(s) for s in index_indicators):
        line, index = split_argument(' '.join(line), short='i', long_='index')
        line, extra_indexes = split_argument(line, long_='extra-index-url')
        package_names = line.split()
        package_name = package_names[0]
        if len(package_names) > 1:
            more_packages = package_names[1:]
        else:
            more_packages = []
    # Capture . argument and assign it to nothing
    if package_name == '.':
        package_name = False
    # Install editable local packages before locking - this givves us acceess to dist-info
    if project.pipfile_exists and (
        not project.lockfile_exists or not project.virtualenv_exists
    ):
        section = project.editable_packages if not dev else project.editable_dev_packages
        for package in section.keys():
            converted = convert_deps_to_pip(
                {package: section[package]}, project=project, r=False
            )
            if not package_name:
                if converted:
                    package_name = converted.pop(0)
            if converted:
                more_packages.extend(converted)
    # Allow more than one package to be provided.
    package_names = [package_name] + more_packages
    # Install all dependencies, if none was provided.
    if package_name is False:
        # Update project settings with pre preference.
        if pre:
            project.update_settings({'allow_prereleases': pre})
        do_init(
            dev=dev,
            allow_global=system,
            ignore_pipfile=ignore_pipfile,
            system=system,
            skip_lock=skip_lock,
            verbose=verbose,
            concurrent=concurrent,
            deploy=deploy,
            pre=pre,
            requirements_dir=requirements_directory,
        )
        requirements_directory.cleanup()
        sys.exit(0)
    # Support for --selective-upgrade.
    if selective_upgrade:
        for i, package_name in enumerate(package_names[:]):
            section = project.packages if not dev else project.dev_packages
            package = convert_deps_from_pip(package_name)
            package__name = list(package.keys())[0]
            package__val = list(package.values())[0]
            try:
                if not is_star(section[package__name]) and is_star(
                    package__val
                ):
                    # Support for VCS dependencies.
                    package_names[i] = convert_deps_to_pip(
                        {package_name: section[package__name]},
                        project=project,
                        r=False,
                    )[
                        0
                    ]
            except KeyError:
                pass
    for package_name in package_names:
        click.echo(
            crayons.normal(
                u'Installing {0}…'.format(
                    crayons.green(package_name, bold=True)
                ),
                bold=True,
            )
        )
        # pip install:
        with spinner():
            c = pip_install(
                package_name,
                ignore_hashes=True,
                allow_global=system,
                selective_upgrade=selective_upgrade,
                no_deps=False,
                verbose=verbose,
                pre=pre,
                requirements_dir=requirements_directory.name,
                index=index,
                extra_indexes=extra_indexes,
            )
            # Warn if --editable wasn't passed.
            try:
                converted = convert_deps_from_pip(package_name)
            except ValueError as e:
                click.echo('{0}: {1}'.format(crayons.red('WARNING'), e))
                requirements_directory.cleanup()
                sys.exit(1)
            key = [k for k in converted.keys()][0]
            if is_vcs(key) or is_vcs(converted[key]) and not converted[
                key
            ].get(
                'editable'
            ):
                click.echo(
                    '{0}: You installed a VCS dependency in non–editable mode. '
                    'This will work fine, but sub-dependencies will not be resolved by {1}.'
                    '\n  To enable this sub–dependency functionality, specify that this dependency is editable.'
                    ''.format(
                        crayons.red('Warning', bold=True),
                        crayons.red('$ pipenv lock'),
                    )
                )
        click.echo(crayons.blue(format_pip_output(c.out)))
        # Ensure that package was successfully installed.
        try:
            assert c.return_code == 0
        except AssertionError:
            click.echo(
                '{0} An error occurred while installing {1}!'.format(
                    crayons.red('Error: ', bold=True),
                    crayons.green(package_name),
                ),
                err=True,
            )
            click.echo(crayons.blue(format_pip_error(c.err)), err=True)
            requirements_directory.cleanup()
            sys.exit(1)
        click.echo(
            '{0} {1} {2} {3}{4}'.format(
                crayons.normal('Adding', bold=True),
                crayons.green(package_name, bold=True),
                crayons.normal("to Pipfile's", bold=True),
                crayons.red(
                    '[dev-packages]' if dev else '[packages]', bold=True
                ),
                crayons.normal('…', bold=True),
            )
        )
        # Add the package to the Pipfile.
        try:
            project.add_package_to_pipfile(package_name, dev)
        except ValueError as e:
            click.echo(
                '{0} {1}'.format(
                    crayons.red('ERROR (PACKAGE NOT INSTALLED):'), e
                )
            )
        # Update project settings with pre preference.
        if pre:
            project.update_settings({'allow_prereleases': pre})
    if lock and not skip_lock:
        do_init(
            dev=dev,
            allow_global=system,
            concurrent=concurrent,
            verbose=verbose,
            keep_outdated=keep_outdated,
            requirements_dir=requirements_directory,
            deploy=deploy,
        )
        requirements_directory.cleanup()