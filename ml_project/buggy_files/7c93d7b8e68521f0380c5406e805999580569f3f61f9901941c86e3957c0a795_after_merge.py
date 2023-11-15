def load_hparams_from_yaml(config_yaml: str, use_omegaconf: bool = True) -> Dict[str, Any]:
    """Load hparams from a file.

        Args:
            config_yaml: Path to config yaml file
            use_omegaconf: If both `OMEGACONF_AVAILABLE` and `use_omegaconf` are True,
                the hparams will be converted to `DictConfig` if possible

    >>> hparams = Namespace(batch_size=32, learning_rate=0.001, data_root='./any/path/here')
    >>> path_yaml = './testing-hparams.yaml'
    >>> save_hparams_to_yaml(path_yaml, hparams)
    >>> hparams_new = load_hparams_from_yaml(path_yaml)
    >>> vars(hparams) == hparams_new
    True
    >>> os.remove(path_yaml)
    """
    fs = get_filesystem(config_yaml)
    if not fs.exists(config_yaml):
        rank_zero_warn(f"Missing Tags: {config_yaml}.", RuntimeWarning)
        return {}

    with fs.open(config_yaml, "r") as fp:
        hparams = yaml.full_load(fp)

    if OMEGACONF_AVAILABLE:
        if use_omegaconf:
            try:
                return OmegaConf.create(hparams)
            except (UnsupportedValueType, ValidationError):
                pass
    return hparams