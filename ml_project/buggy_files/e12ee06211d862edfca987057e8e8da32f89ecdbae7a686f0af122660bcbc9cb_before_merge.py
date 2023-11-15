def add_pip_installed(prefix, installed_pkgs, json=None, output=True):
    # Defer to json for backwards compatibility
    if type(json) is bool:
        output = not json

    # TODO Refactor so installed is a real list of objects/dicts
    #      instead of strings allowing for direct comparison
    conda_names = {d.rsplit('-', 2)[0] for d in installed_pkgs}

    for pip_pkg in installed(prefix, output=output):
        if pip_pkg['name'] in conda_names and not 'path' in pip_pkg:
            continue
        installed_pkgs.add(str(pip_pkg))