def _parse_params(path_params):
    from ruamel.yaml import YAMLError

    from dvc.dependency.param import ParamsDependency
    from dvc.utils.flatten import unflatten
    from dvc.utils.serialize import loads_yaml

    ret = {}
    for path_param in path_params:
        path, _, params_str = path_param.rpartition(":")
        # remove empty strings from params, on condition such as `-p "file1:"`
        params = {}
        for param_str in filter(bool, params_str.split(",")):
            try:
                # interpret value strings using YAML rules
                key, value = param_str.split("=")
                params[key] = loads_yaml(value)
            except (ValueError, YAMLError):
                raise InvalidArgumentError(
                    f"Invalid param/value pair '{param_str}'"
                )
        if not path:
            path = ParamsDependency.DEFAULT_PARAMS_FILE
        ret[path] = unflatten(params)
    return ret