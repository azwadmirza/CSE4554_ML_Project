def get_converted_relative_path(path, relative_to=os.curdir):
    """Given a vague relative path, return the path relative to the given location"""
    relpath = os.path.relpath(path, start=relative_to)
    if os.name == 'nt':
        return os.altsep.join([".", relpath])
    return os.path.join(".", relpath)