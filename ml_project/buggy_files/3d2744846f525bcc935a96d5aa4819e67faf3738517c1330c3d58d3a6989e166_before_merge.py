    def cache_key(
        cls, component_meta: Dict[Text, Any], model_metadata: Metadata
    ) -> Optional[Text]:
        _config = common.update_existing_keys(cls.defaults, component_meta)
        return f"{cls.name}-{get_dict_hash(_config)}"