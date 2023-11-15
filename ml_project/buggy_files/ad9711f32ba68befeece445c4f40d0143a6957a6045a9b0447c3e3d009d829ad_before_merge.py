def expand_path_vars(path: str) -> str:
    """Expand the environment or ~ variables in a path string."""
    path = path.strip()
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    return path