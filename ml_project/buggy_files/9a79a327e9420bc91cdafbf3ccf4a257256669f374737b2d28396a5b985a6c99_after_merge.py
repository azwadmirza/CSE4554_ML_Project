def write(filename, data, env=None):
    """Writes `data` to `filename` infers format by file extension."""
    loader_name = "{0}_loader".format(filename.rpartition(".")[-1])
    loader = globals().get(loader_name)
    if not loader:
        raise IOError("{0} cannot be found.".format(loader_name))

    data = DynaBox(data).to_dict()
    if loader is not py_loader and env and env not in data:
        data = {env: data}

    loader.write(filename, data, merge=False)