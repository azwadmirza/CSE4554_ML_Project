def save_hparams_to_yaml(config_yaml, hparams: Union[dict, Namespace]) -> None:
    """
    Args:
        config_yaml: path to new YAML file
        hparams: parameters to be saved
    """
    if not gfile.isdir(os.path.dirname(config_yaml)):
        raise RuntimeError(f"Missing folder: {os.path.dirname(config_yaml)}.")

    if OMEGACONF_AVAILABLE and isinstance(hparams, Container):
        from omegaconf import OmegaConf

        OmegaConf.save(hparams, config_yaml, resolve=True)
        return

    # saving the standard way
    if isinstance(hparams, Namespace):
        hparams = vars(hparams)
    elif isinstance(hparams, AttributeDict):
        hparams = dict(hparams)
    assert isinstance(hparams, dict)

    with cloud_open(config_yaml, "w", newline="") as fp:
        yaml.dump(hparams, fp)