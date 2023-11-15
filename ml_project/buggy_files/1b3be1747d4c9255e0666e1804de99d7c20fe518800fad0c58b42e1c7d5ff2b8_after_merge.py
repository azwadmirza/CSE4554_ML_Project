def _get_package_info(name, saltenv='base'):
    '''
    Return package info.
    Returns empty map if package not available
    TODO: Add option for version
    '''
    return get_repo_data(saltenv).get('repo', {}).get(name, {})