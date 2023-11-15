def to_single_stage_lockfile(stage: "Stage") -> dict:
    assert stage.cmd

    res = OrderedDict([("cmd", stage.cmd)])
    params, deps = split_params_deps(stage)
    deps, outs = [
        [
            OrderedDict(
                [
                    (PARAM_PATH, item.def_path),
                    (item.checksum_type, item.checksum),
                ]
            )
            for item in sort_by_path(items)
        ]
        for items in [deps, stage.outs]
    ]
    params = _serialize_params_values(params)
    if deps:
        res[PARAM_DEPS] = deps
    if params:
        res[PARAM_PARAMS] = params
    if outs:
        res[PARAM_OUTS] = outs

    return res