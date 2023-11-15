def path_as_uri(path):
    return pathlib.Path(osp.abspath(path)).as_uri()