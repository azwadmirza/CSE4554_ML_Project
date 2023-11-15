def path_as_uri(path):
    path_obj = pathlib.Path(osp.abspath(path))
    if os.name == 'nt' and PY2:
        return make_as_uri(path_obj)
    else:
        return path_obj.as_uri()