    def cache_key(
        cls, component_meta: Dict[Text, Any], model_metadata: Metadata
    ) -> Optional[Text]:
        """Cache the component for future use.

        Args:
            component_meta: configuration for the component.
            model_metadata: configuration for the whole pipeline.

        Returns: key of the cache for future retrievals.
        """
        _config = common.update_existing_keys(cls.defaults, component_meta)
        return f"{cls.name}-{get_dict_hash(_config)}"