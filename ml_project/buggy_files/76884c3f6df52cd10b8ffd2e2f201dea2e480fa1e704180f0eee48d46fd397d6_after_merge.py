    def __delitem__(self, key: DictKeyType) -> None:
        key = self._validate_and_normalize_key(key)
        if self._get_flag("readonly"):
            self._format_and_raise(
                key=key,
                value=None,
                cause=ReadonlyConfigError(
                    "DictConfig in read-only mode does not support deletion"
                ),
            )
        if self._get_flag("struct"):
            self._format_and_raise(
                key=key,
                value=None,
                cause=ConfigTypeError(
                    "DictConfig in struct mode does not support deletion"
                ),
            )
        if self._is_typed() and self._get_node_flag("struct") is not False:
            self._format_and_raise(
                key=key,
                value=None,
                cause=ConfigTypeError(
                    f"{type_str(self._metadata.object_type)} (DictConfig) does not support deletion"
                ),
            )

        try:
            del self.__dict__["_content"][key]
        except KeyError:
            msg = "Key not found: '$KEY'"
            self._format_and_raise(key=key, value=None, cause=ConfigKeyError(msg))