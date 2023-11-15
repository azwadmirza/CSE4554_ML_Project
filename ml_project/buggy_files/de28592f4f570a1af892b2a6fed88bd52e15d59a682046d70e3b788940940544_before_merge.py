    def show_cfg(self, overrides, cfg_type):
        assert cfg_type in ["job", "hydra", "all"]
        cfg = self.compose_config(overrides, with_log_configuration=True)
        if cfg_type == "job":
            del cfg["hydra"]
        elif cfg_type == "hydra":
            cfg = self.get_sanitized_hydra_cfg(cfg)
        print(cfg.pretty())