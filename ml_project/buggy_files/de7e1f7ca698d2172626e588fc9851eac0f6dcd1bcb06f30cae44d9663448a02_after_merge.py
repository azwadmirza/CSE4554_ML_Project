def list_all(resolve=False):
    """Return the list of vendored projects."""
    # TODO: Derive from os.listdir(VENDORED_ROOT)?
    projects = ["pydevd"]
    if not resolve:
        return projects
    return [project_root(name) for name in projects]