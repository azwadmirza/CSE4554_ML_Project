def _to_schema_column_or_string(element):
    if element is None:
        return element
    elif hasattr(element, "__clause_element__"):
        element = element.__clause_element__()
    if not isinstance(element, util.string_types + (ColumnElement,)):
        msg = "Element %r is not a string name or column element"
        raise exc.ArgumentError(msg % element)
    return element