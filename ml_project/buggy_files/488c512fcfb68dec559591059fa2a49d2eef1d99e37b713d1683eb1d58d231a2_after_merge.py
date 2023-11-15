    def _get_key_factory(self, by_alias: bool) -> Callable[..., str]:
        if by_alias:
            return lambda fields, key: fields[key].alias if key in fields else key

        return lambda _, key: key