def save_hparams_to_yaml(config_yaml, hparams: Union[dict, Namespace]) -> None:
    """
    Args:
        config_yaml: path to new YAML file
        hparams: parameters to be saved
    """
    fs = get_filesystem(config_yaml)
    if not fs.isdir(os.path.dirname(config_yaml)):
        raise RuntimeError(f"Missing folder: {os.path.dirname(config_yaml)}.")

    # convert Namespace or AD to dict
    if isinstance(hparams, Namespace):
        hparams = vars(hparams)
    elif isinstance(hparams, AttributeDict):
        hparams = dict(hparams)

    # saving with OmegaConf objects
    if OMEGACONF_AVAILABLE:
        if OmegaConf.is_config(hparams):
            with fs.open(config_yaml, "w", encoding="utf-8") as fp:
                OmegaConf.save(hparams, fp, resolve=True)
            return
        for v in hparams.values():
            if OmegaConf.is_config(v):
                with fs.open(config_yaml, "w", encoding="utf-8") as fp:
                    OmegaConf.save(OmegaConf.create(hparams), fp, resolve=True)
                return

    assert isinstance(hparams, dict)
    hparams_allowed = {}
    # drop paramaters which contain some strange datatypes as fsspec
    for k, v in hparams.items():
        try:
            yaml.dump(v)
        except TypeError as err:
            warn(f"Skipping '{k}' parameter because it is not possible to safely dump to YAML.")
            hparams[k] = type(v).__name__
        else:
            hparams_allowed[k] = v

    # saving the standard way
    with fs.open(config_yaml, "w", newline="") as fp:
        yaml.dump(hparams_allowed, fp)