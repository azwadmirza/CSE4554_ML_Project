def _follow_field_source(model, path: List[str]):
    """
        navigate through root model via given navigation path. supports forward/reverse relations.
    """
    field_or_property = getattr(model, path[0], None)

    if len(path) == 1:
        # end of traversal
        if isinstance(field_or_property, property):
            return field_or_property.fget
        elif isinstance(field_or_property, cached_property):
            return field_or_property.func
        elif callable(field_or_property):
            return field_or_property
        elif isinstance(field_or_property, ManyToManyDescriptor):
            if field_or_property.reverse:
                return field_or_property.rel.target_field  # m2m reverse
            else:
                return field_or_property.field.target_field  # m2m forward
        elif isinstance(field_or_property, ReverseOneToOneDescriptor):
            return field_or_property.related.target_field  # o2o reverse
        elif isinstance(field_or_property, ReverseManyToOneDescriptor):
            return field_or_property.rel.target_field  # type: ignore # foreign reverse
        elif isinstance(field_or_property, ForwardManyToOneDescriptor):
            return field_or_property.field.target_field  # type: ignore # o2o & foreign forward
        else:
            field = model._meta.get_field(path[0])
            if isinstance(field, ForeignObjectRel):
                # case only occurs when relations are traversed in reverse and
                # not via the related_name (default: X_set) but the model name.
                return field.target_field
            else:
                return field
    else:
        if isinstance(field_or_property, property) or callable(field_or_property):
            if isinstance(field_or_property, property):
                target_model = typing.get_type_hints(field_or_property.fget).get('return')
            else:
                target_model = typing.get_type_hints(field_or_property).get('return')
            if not target_model:
                raise UnableToProceedError(
                    f'could not follow field source through intermediate property "{path[0]}" '
                    f'on model {model}. please add a type hint on the model\'s property/function '
                    f'to enable traversal of the source path "{".".join(path)}".'
                )
            return _follow_field_source(target_model, path[1:])
        else:
            target_model = model._meta.get_field(path[0]).related_model
            return _follow_field_source(target_model, path[1:])