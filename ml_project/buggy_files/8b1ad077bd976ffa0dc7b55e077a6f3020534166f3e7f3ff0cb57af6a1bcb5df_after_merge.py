def get_annotation_from_schema(annotation: Any, schema: Schema) -> Type[Any]:
    """
    Get an annotation with validation implemented for numbers and strings based on the schema.

    :param annotation: an annotation from a field specification, as ``str``, ``ConstrainedStr``
    :param schema: an instance of Schema, possibly with declarations for validations and JSON Schema
    :return: the same ``annotation`` if unmodified or a new annotation with validation in place
    """
    if isinstance(annotation, type):
        attrs: Optional[Tuple[str, ...]] = None
        constraint_func: Optional[Callable[..., type]] = None
        if issubclass(annotation, str) and not issubclass(annotation, (EmailStr, AnyUrl, ConstrainedStr)):
            attrs = ('max_length', 'min_length', 'regex')
            constraint_func = constr
        elif lenient_issubclass(annotation, numeric_types) and not issubclass(
            annotation, (ConstrainedInt, ConstrainedFloat, ConstrainedDecimal, ConstrainedList, bool)
        ):
            # Is numeric type
            attrs = ('gt', 'lt', 'ge', 'le', 'multiple_of')
            numeric_type = next(t for t in numeric_types if issubclass(annotation, t))  # pragma: no branch
            constraint_func = _map_types_constraint[numeric_type]
        elif issubclass(annotation, ConstrainedList):
            attrs = ('min_items', 'max_items')
            constraint_func = conlist
        if attrs:
            kwargs = {
                attr_name: attr
                for attr_name, attr in ((attr_name, getattr(schema, attr_name)) for attr_name in attrs)
                if attr is not None
            }
            if kwargs:
                constraint_func = cast(Callable[..., type], constraint_func)
                return constraint_func(**kwargs)
    return annotation