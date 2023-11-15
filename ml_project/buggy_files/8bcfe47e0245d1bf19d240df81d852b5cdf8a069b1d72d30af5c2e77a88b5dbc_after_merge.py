def do_download_dependencies(dev=False, only=False, bare=False):
    """"Executes the download functionality."""

    # Load the Lockfile.
    lockfile = split_vcs(project._lockfile)

    if not bare:
        click.echo(crayons.yellow('Downloading dependencies from Pipfile...'))

    # Install default dependencies, always.
    deps = lockfile['default'] if not only else {}

    # Add development deps if --dev was passed.
    if dev:
        deps.update(lockfile['develop'])

    # Convert the deps to pip-compatible arguments.
    deps = convert_deps_to_pip(deps, r=False)

    # Certain Windows/Python combinations return lower-cased file names
    # to console output, despite downloading the properly cased file.
    # We'll use Requests' CaseInsensitiveDict to address this.
    names_map = requests.structures.CaseInsensitiveDict()

    # Actually install each dependency into the virtualenv.
    for package_name in deps:

        if not bare:
            click.echo('Downloading {0}...'.format(crayons.green(package_name)))

        # pip install:
        c = pip_download(package_name)

        if not bare:
            click.echo(crayons.blue(c.out))

        parsed_output = parse_install_output(c.out)
        for filename, name in parsed_output:
            names_map[filename] = name

    return names_map