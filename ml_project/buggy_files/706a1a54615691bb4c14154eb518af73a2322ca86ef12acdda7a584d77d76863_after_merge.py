    def __call__(self, conf: "Config", name: Optional[str], loaders: List[Loader[T]], chain: List[str]) -> T:
        if self._cache is _PLACE_HOLDER:
            found = False
            for key in self.keys:
                for loader in loaders:
                    try:
                        value = loader.load(key, self.of_type, self.kwargs, conf, self.env_name, chain)
                        found = True
                    except KeyError:
                        continue
                    break
                if found:
                    break
            else:
                value = self.default(conf, self.env_name) if callable(self.default) else self.default
            if self.post_process is not None:
                value = self.post_process(value, conf)  # noqa
            self._cache = value
        return cast(T, self._cache)