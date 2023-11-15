def list_items(module, base, command):
    """List package info based on the command."""
    # Rename updates to upgrades
    if command == 'updates':
        command = 'upgrades'

    # Return the corresponding packages
    if command in ['installed', 'upgrades', 'available']:
        results = [
            _package_dict(package)
            for package in getattr(base.sack.query(), command)()]
    # Return the enabled repository ids
    elif command in ['repos', 'repositories']:
        results = [
            {'repoid': repo.id, 'state': 'enabled'}
            for repo in base.repos.iter_enabled()]
    # Return any matching packages
    else:
        packages = subject.Subject(command).get_best_query(base.sack)
        results = [_package_dict(package) for package in packages]

    module.exit_json(results=results)