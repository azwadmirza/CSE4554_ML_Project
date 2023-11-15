    def __str__(self) -> str:
        permitted = ', '.join(repr(v.value) for v in self.ctx['enum_values'])  # type: ignore
        return f'value is not a valid enumeration member; permitted: {permitted}'