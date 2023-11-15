    def _resolve_with_default(
        self,
        key: Union[DictKeyType, int],
        value: Any,
        default_value: Any = DEFAULT_VALUE_MARKER,
    ) -> Any:
        """returns the value with the specified key, like obj.key and obj['key']"""

        def is_mandatory_missing(val: Any) -> bool:
            return bool(get_value_kind(val) == ValueKind.MANDATORY_MISSING)

        val = _get_value(value)
        has_default = default_value is not DEFAULT_VALUE_MARKER
        if has_default and (val is None or is_mandatory_missing(val)):
            return default_value

        resolved = self._maybe_resolve_interpolation(
            parent=self,
            key=key,
            value=value,
            throw_on_missing=not has_default,
            throw_on_resolution_failure=not has_default,
        )
        if resolved is None and has_default:
            return default_value

        if is_mandatory_missing(resolved):
            if has_default:
                return default_value
            else:
                raise MissingMandatoryValue("Missing mandatory value: $FULL_KEY")

        return _get_value(resolved)