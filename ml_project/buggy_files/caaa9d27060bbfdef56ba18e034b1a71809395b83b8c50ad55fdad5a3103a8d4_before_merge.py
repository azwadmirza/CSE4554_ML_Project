def project_root(project):
    """Return the path the root dir of the vendored project.

    If "project" is an empty string then the path prefix for vendored
    projects (e.g. "debugpy/_vendored/") will be returned.
    """
    if not project:
        project = ''
    return os.path.join(VENDORED_ROOT, project)