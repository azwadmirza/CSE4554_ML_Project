    def _merge_defaults(self, cfg, defaults, split_at):
        def get_filename(config_name):
            filename, ext = os.path.splitext(config_name)
            if ext == "":
                ext = ".yaml"
            return "{}{}".format(filename, ext)

        def merge_defaults(merged_cfg, def_list):
            cfg_with_list = OmegaConf.create(dict(defaults=def_list))
            for default1 in cfg_with_list.defaults:
                if isinstance(default1, DictConfig):
                    is_optional = False
                    if default1.optional is not None:
                        is_optional = default1.optional
                        del default1["optional"]
                    family = next(iter(default1.keys()))
                    name = default1[family]
                    # Name is none if default value is removed
                    if name is not None and "_SKIP_" not in name:
                        merged_cfg = self._merge_config(
                            cfg=merged_cfg,
                            family=family,
                            name=get_filename(name),
                            required=not is_optional,
                        )
                else:
                    assert isinstance(default1, str)
                    if "_SKIP_" not in default1:
                        merged_cfg = self._merge_config(
                            cfg=merged_cfg,
                            family="",
                            name=get_filename(default1),
                            required=True,
                        )
            return merged_cfg

        system_list = []
        user_list = []
        for default in defaults:
            if len(system_list) < split_at:
                system_list.append(default)
            else:
                user_list.append(default)
        cfg = merge_defaults(cfg, system_list)
        cfg = merge_defaults(cfg, user_list)

        if "defaults" in cfg:
            del cfg["defaults"]
        return cfg