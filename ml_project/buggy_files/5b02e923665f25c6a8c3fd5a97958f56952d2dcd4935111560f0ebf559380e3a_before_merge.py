def strict_str_validator(v: Any) -> str:
    if isinstance(v, str):
        return v
    raise errors.StrError()