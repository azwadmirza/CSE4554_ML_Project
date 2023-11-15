    def get(self, key: str, of_type: Type[Any]) -> Any:
        cache_key = key, of_type
        if cache_key in self._cache:
            result = self._cache[cache_key]
        else:
            try:
                if self.ini is None:  # pragma: no cover # this can only happen if we don't call __bool__ firsts
                    result = None
                else:
                    source = "file"
                    value = self.ini.load(key, of_type=of_type, conf=None, env_name="tox", chain=[key])
                    result = value, source
            except KeyError:  # just not found
                result = None
            except Exception as exception:  # noqa
                logging.warning("%s key %s as type %r failed with %r", self.config_file, key, of_type, exception)
                result = None
        self._cache[cache_key] = result
        return result