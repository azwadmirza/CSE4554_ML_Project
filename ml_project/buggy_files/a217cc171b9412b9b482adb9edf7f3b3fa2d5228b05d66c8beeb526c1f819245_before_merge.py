    def _s_validate_and_normalize_key(self, key_type: Any, key: Any) -> DictKeyType:
        if key_type is Any:
            for t in DictKeyType.__args__:  # type: ignore
                try:
                    return self._s_validate_and_normalize_key(key_type=t, key=key)
                except KeyValidationError:
                    pass
            raise KeyValidationError("Incompatible key type '$KEY_TYPE'")
        elif key_type == str:
            if not isinstance(key, str):
                raise KeyValidationError(
                    f"Key $KEY ($KEY_TYPE) is incompatible with ({key_type.__name__})"
                )

            return key
        elif key_type == int:
            if not isinstance(key, int):
                raise KeyValidationError(
                    f"Key $KEY ($KEY_TYPE) is incompatible with ({key_type.__name__})"
                )

            return key
        elif issubclass(key_type, Enum):
            try:
                ret = EnumNode.validate_and_convert_to_enum(key_type, key)
                assert ret is not None
                return ret
            except ValidationError:
                valid = ", ".join([x for x in key_type.__members__.keys()])
                raise KeyValidationError(
                    f"Key '$KEY' is incompatible with the enum type '{key_type.__name__}', valid: [{valid}]"
                )
        else:
            assert False, f"Unsupported key type {key_type}"