def log_parameters_lite(log_file, args):
    log_params = {}
    for param_name, param_value in args.__dict__.items():
        log_params[param_name] = param_value
    if args.args_data is not None:
        stub_method = pickle.loads(base64.b64decode(args.args_data))
        method_args = stub_method.kwargs
        log_params["json_args"] = dict()
        for k, v in list(method_args.items()):
            log_params["json_args"][k] = stub_to_json(v)
        kwargs = stub_method.obj.kwargs
        for k in ["baseline", "env", "policy"]:
            if k in kwargs:
                log_params["json_args"][k] = stub_to_json(kwargs.pop(k))
        log_params["json_args"]["algo"] = stub_to_json(stub_method.obj)
    mkdir_p(os.path.dirname(log_file))
    with open(log_file, "w") as f:
        json.dump(log_params, f, indent=2, sort_keys=True, cls=MyEncoder)