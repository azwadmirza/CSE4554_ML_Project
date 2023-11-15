    def add_config(
        self,
        keys: Union[str, Sequence[str]],
        of_type: Type[V],
        default: Union[Callable[["Config", Optional[str]], V], V],
        desc: str,
        post_process: Optional[Callable[[V, "Config"], V]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
    ) -> ConfigDynamicDefinition[V]:
        """
        Add configuration value.
        """
        keys_ = self._make_keys(keys)
        definition = ConfigDynamicDefinition(keys_, desc, self._name, of_type, default, post_process, kwargs)
        result = self._add_conf(keys_, definition)
        return cast(ConfigDynamicDefinition[V], result)