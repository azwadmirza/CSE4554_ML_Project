def get_converted_relative_path(path, relative_to=os.curdir):
    """Given a vague relative path, return the path relative to the given location"""
    return os.path.join(".", os.path.relpath(path, start=relative_to))