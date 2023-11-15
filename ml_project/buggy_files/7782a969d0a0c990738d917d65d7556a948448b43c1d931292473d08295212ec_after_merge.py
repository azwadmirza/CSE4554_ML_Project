def _get_kwargs(config: Union[ObjectConf, DictConfig], **kwargs: Any) -> Any:
    # copy config to avoid mutating it when merging with kwargs
    config_copy = copy.deepcopy(config)

    # Manually set parent as deepcopy does not currently handles it (https://github.com/omry/omegaconf/issues/130)
    # noinspection PyProtectedMember
    config_copy._set_parent(config._get_parent())  # type: ignore
    config = config_copy

    params = config.params if "params" in config else OmegaConf.create()
    assert isinstance(
        params, DictConfig
    ), f"Input config params are expected to be a mapping, found {type(config.params).__name__}"
    primitives = {}
    rest = {}
    for k, v in kwargs.items():
        if _utils.is_primitive_type(v) or isinstance(v, (dict, list)):
            primitives[k] = v
        else:
            rest[k] = v
    final_kwargs = {}
    with read_write(params):
        params.merge_with(OmegaConf.create(primitives))

    for k, v in params.items():
        final_kwargs[k] = v

    for k, v in rest.items():
        final_kwargs[k] = v
    return final_kwargs