    def _s_validate_and_normalize_key(self, key_type: Any, key: Any) -> DictKeyType:
        if key_type is Any:
            for t in DictKeyType.__args__:  # type: ignore
                if isinstance(key, t):
                    return key  # type: ignore
            raise KeyValidationError("Incompatible key type '$KEY_TYPE'")
        elif key_type is bool and key in [0, 1]:
            # Python treats True as 1 and False as 0 when used as dict keys
            #   assert hash(0) == hash(False)
            #   assert hash(1) == hash(True)
            return bool(key)
        elif key_type in (str, int, float, bool):  # primitive type
            if not isinstance(key, key_type):
                raise KeyValidationError(
                    f"Key $KEY ($KEY_TYPE) is incompatible with ({key_type.__name__})"
                )

            return key  # type: ignore
        elif issubclass(key_type, Enum):
            try:
                ret = EnumNode.validate_and_convert_to_enum(
                    key_type, key, allow_none=False
                )
                assert ret is not None
                return ret
            except ValidationError:
                valid = ", ".join([x for x in key_type.__members__.keys()])
                raise KeyValidationError(
                    f"Key '$KEY' is incompatible with the enum type '{key_type.__name__}', valid: [{valid}]"
                )
        else:
            assert False, f"Unsupported key type {key_type}"