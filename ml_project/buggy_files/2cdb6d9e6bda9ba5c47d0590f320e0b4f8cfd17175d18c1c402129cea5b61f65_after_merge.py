    def _compose_config_from_defaults_list(
        self,
        defaults: List[ResultDefault],
        repo: IConfigRepository,
    ) -> DictConfig:
        cfg = OmegaConf.create()
        with flag_override(cfg, "no_deepcopy_set_nodes", True):
            for default in defaults:
                loaded = self._load_single_config(default=default, repo=repo)
                try:
                    cfg.merge_with(loaded.config)
                except ValidationError as e:
                    raise ConfigCompositionException(
                        f"In '{default.config_path}': Validation error while composing config:\n{e}"
                    ).with_traceback(sys.exc_info()[2])

        # This is primarily cosmetic
        cfg._metadata.ref_type = cfg._metadata.object_type

        return cfg