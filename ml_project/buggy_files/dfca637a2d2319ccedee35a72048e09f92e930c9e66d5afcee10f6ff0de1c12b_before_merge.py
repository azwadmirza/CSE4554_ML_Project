def get_original_cwd() -> str:
    """
    :return: the original working directory the Hydra application was launched from
    """
    hc = HydraConfig.instance()
    if hc.hydra is None:
        raise ValueError(
            "get_original_cwd() must only be used after HydraConfig is initialized"
        )
    ret = hc.hydra.runtime.cwd
    assert ret is not None and isinstance(ret, str)
    return ret