def save_hparams_to_yaml(config_yaml, hparams: Union[dict, Namespace]) -> None:
    """
    Args:
        config_yaml: path to new YAML file
        hparams: parameters to be saved
    """
    if not gfile.isdir(os.path.dirname(config_yaml)):
        raise RuntimeError(f"Missing folder: {os.path.dirname(config_yaml)}.")

    # convert Namespace or AD to dict
    if isinstance(hparams, Namespace):
        hparams = vars(hparams)
    elif isinstance(hparams, AttributeDict):
        hparams = dict(hparams)

    # saving with OmegaConf objects
    if OmegaConf is not None:
        if OmegaConf.is_config(hparams):
            OmegaConf.save(hparams, config_yaml, resolve=True)
            return
        for v in hparams.values():
            if OmegaConf.is_config(v):
                OmegaConf.save(OmegaConf.create(hparams), config_yaml, resolve=True)
                return

    # saving the standard way
    assert isinstance(hparams, dict)
    with open(config_yaml, 'w', newline='') as fp:
        yaml.dump(hparams, fp)