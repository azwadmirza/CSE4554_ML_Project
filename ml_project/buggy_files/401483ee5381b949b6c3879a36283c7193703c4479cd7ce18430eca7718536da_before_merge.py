def call(
    config: Union[ObjectConf, TargetConf, DictConfig, Dict[Any, Any]],
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    :param config: An object describing what to call and what params to use
    :param args: optional positional parameters pass-through
    :param kwargs: optional named parameters pass-through
    :return: the return value from the specified class or method
    """
    if isinstance(config, TargetConf) and config._target_ == "???":
        raise InstantiationException(
            f"Missing _target_ value. Check that you specified it in '{type(config).__name__}'"
            f" and that the type annotation is correct: '_target_: str = ...'"
        )
    if isinstance(config, (dict, ObjectConf, TargetConf)):
        config = OmegaConf.structured(config)

    if OmegaConf.is_none(config):
        return None
    cls = "<unknown>"
    try:
        assert isinstance(config, DictConfig)
        # make a copy to ensure we do not change the provided object
        config = copy.deepcopy(config)
        OmegaConf.set_readonly(config, False)
        OmegaConf.set_struct(config, False)
        cls = _get_cls_name(config)
        type_or_callable = _locate(cls)
        if isinstance(type_or_callable, type):
            return _instantiate_class(type_or_callable, config, *args, **kwargs)
        else:
            assert callable(type_or_callable)
            return _call_callable(type_or_callable, config, *args, **kwargs)
    except InstantiationException as e:
        raise e
    except Exception as e:
        raise HydraException(f"Error calling '{cls}' : {e}") from e