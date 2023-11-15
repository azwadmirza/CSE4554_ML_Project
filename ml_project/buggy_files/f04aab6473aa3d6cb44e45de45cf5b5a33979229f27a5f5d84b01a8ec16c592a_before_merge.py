def _make_subclass(name: str, module: str, superclass: Any = _MockObject,
                   attributes: Any = None) -> Any:
    attrs = {'__module__': module, '__display_name__': module + '.' + name}
    attrs.update(attributes or {})

    return type(name, (superclass,), attrs)