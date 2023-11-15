def resolve_deps(deps, which, which_pip, project, sources=None, verbose=False, python=False, clear=False, pre=False, allow_global=False):
    """Given a list of dependencies, return a resolved list of dependencies,
    using pip-tools -- and their hashes, using the warehouse API / pip.
    """

    index_lookup = {}
    markers_lookup = {}

    python_path = which('python', allow_global=allow_global)
    backup_python_path = shellquote(sys.executable)

    results = []

    # First (proper) attempt:
    with HackedPythonVersion(python_version=python, python_path=python_path):

        try:
            resolved_tree, resolver = actually_resolve_reps(deps, index_lookup, markers_lookup, project, sources, verbose, clear, pre)
        except RuntimeError:
            # Don't exit here, like usual.
            resolved_tree = None

    # Second (last-resort) attempt:
    if resolved_tree is None:
        with HackedPythonVersion(python_version='.'.join([str(s) for s in sys.version_info[:3]]), python_path=backup_python_path):

            try:
                # Attempt to resolve again, with different Python version information,
                # particularly for particularly particular packages.
                resolved_tree, resolver = actually_resolve_reps(deps, index_lookup, markers_lookup, project, sources, verbose, clear, pre)
            except RuntimeError:
                sys.exit(1)


    for result in resolved_tree:
        if not result.editable:
            name = pep423_name(result.name)
            version = clean_pkg_version(result.specifier)
            index = index_lookup.get(result.name)

            if not markers_lookup.get(result.name):
                markers = str(result.markers) if result.markers and 'extra' not in str(result.markers) else None
            else:
                markers = markers_lookup.get(result.name)

            collected_hashes = []
            if 'python.org' in '|'.join([source['url'] for source in sources]):
                try:
                    # Grab the hashes from the new warehouse API.
                    r = requests.get('https://pypi.org/pypi/{0}/json'.format(name), timeout=10)
                    api_releases = r.json()['releases']

                    cleaned_releases = {}
                    for api_version, api_info in api_releases.items():
                        cleaned_releases[clean_pkg_version(api_version)] = api_info

                    for release in cleaned_releases[version]:
                        collected_hashes.append(release['digests']['sha256'])

                    collected_hashes = ['sha256:' + s for s in collected_hashes]

                    # Collect un-collectable hashes.
                    if not collected_hashes:
                        collected_hashes = list(list(resolver.resolve_hashes([result]).items())[0][1])

                except (ValueError, KeyError, ConnectionError):
                    if verbose:
                        print('Error fetching {}'.format(name))

            d = {'name': name, 'version': version, 'hashes': collected_hashes}

            if index:
                d.update({'index': index})

            if markers:
                d.update({'markers': markers.replace('"', "'")})

            results.append(d)

    return results