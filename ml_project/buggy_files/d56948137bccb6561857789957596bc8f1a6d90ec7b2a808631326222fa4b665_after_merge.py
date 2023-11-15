    def to_container(
        cfg: Any,
        *,
        resolve: bool = False,
        enum_to_str: bool = False,
        exclude_structured_configs: bool = False,
    ) -> Union[Dict[DictKeyType, Any], List[Any], None, str]:
        """
        Resursively converts an OmegaConf config to a primitive container (dict or list).
        :param cfg: the config to convert
        :param resolve: True to resolve all values
        :param enum_to_str: True to convert Enum values to strings
        :param exclude_structured_configs: If True, do not convert Structured Configs
               (DictConfigs backed by a dataclass)
        :return: A dict or a list representing this config as a primitive container.
        """
        if not OmegaConf.is_config(cfg):
            raise ValueError(
                f"Input cfg is not an OmegaConf config object ({type_str(type(cfg))})"
            )

        return BaseContainer._to_content(
            cfg,
            resolve=resolve,
            enum_to_str=enum_to_str,
            exclude_structured_configs=exclude_structured_configs,
        )