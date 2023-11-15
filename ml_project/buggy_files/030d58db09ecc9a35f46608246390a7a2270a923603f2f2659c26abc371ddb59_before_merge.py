    def load(
        self, key: str, of_type: Type[V], conf: Optional["Config"], env_name: Optional[str], chain: List[str]
    ) -> V:
        """
        Load a value.

        :param key: the key under it lives
        :param of_type: the type to convert to
        :param conf: the configuration object of this tox session (needed to manifest the value)
        :param env_name: env name
        :return: the converted type
        """
        if key in self.overrides:
            return _STR_CONVERT.to(self.overrides[key].value, of_type)
        raw = self.load_raw(key, conf, env_name)
        future: "Future[V]" = Future()
        with self.build(future, key, of_type, conf, env_name, raw, chain) as prepared:
            converted = self.to(prepared, of_type)
            future.set_result(converted)
        return converted