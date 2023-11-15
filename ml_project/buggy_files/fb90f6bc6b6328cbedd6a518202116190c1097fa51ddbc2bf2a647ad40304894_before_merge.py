def _process_type(
    cls, *, name=None, is_input=False, is_interface=False, description=None
):
    name = name or cls.__name__

    def _get_fields(wrapped, types_replacement_map=None):
        class_fields = dataclasses.fields(wrapped)

        fields = {}

        for class_field in class_fields:
            # we want to make a copy of the original field when dealing
            # with generic types and also get the actual type for the type var
            if is_type_var(class_field.type) or has_type_var(class_field.type):
                class_field = copy.copy(class_field)
                class_field.type = get_actual_type(
                    class_field.type, types_replacement_map
                )
            # like args, a None default implies Optional
            if class_field.default is None:
                class_field.type = Optional[class_field.type]

            field_name = getattr(class_field, "field_name", None) or to_camel_case(
                class_field.name
            )
            description = getattr(class_field, "field_description", None)
            permission_classes = getattr(class_field, "field_permission_classes", None)
            resolver = getattr(class_field, "field_resolver", None) or _get_resolver(
                cls, class_field.name
            )
            resolver.__annotations__["return"] = class_field.type

            fields[field_name] = field(
                resolver,
                is_input=is_input,
                description=description,
                permission_classes=permission_classes,
            ).graphql_type
            # supply a graphql default_value if the type annotation has a default
            if class_field.default not in (dataclasses.MISSING, None):
                fields[field_name].default_value = class_field.default

        strawberry_fields = {}

        for base in [cls, *cls.__bases__]:
            strawberry_fields.update(
                {
                    key: value
                    for key, value in base.__dict__.items()
                    if getattr(value, IS_STRAWBERRY_FIELD, False)
                }
            )

        for key, value in strawberry_fields.items():
            name = getattr(value, "field_name", None) or to_camel_case(key)

            fields[name] = value.graphql_type

        return fields

    if is_input:
        setattr(cls, IS_STRAWBERRY_INPUT, True)
    elif is_interface:
        setattr(cls, IS_STRAWBERRY_INTERFACE, True)

    extra_kwargs = {"description": description or cls.__doc__}

    wrapped = dataclasses.dataclass(cls)

    if is_input:
        TypeClass = GraphQLInputObjectType
    elif is_interface:
        TypeClass = GraphQLInterfaceType

        # TODO: in future we might want to be able to override this
        # for example to map a class (like a django model) to one
        # type of the interface
        extra_kwargs["resolve_type"] = _interface_resolve_type
    else:
        TypeClass = GraphQLObjectType

        extra_kwargs["interfaces"] = [
            klass.graphql_type
            for klass in cls.__bases__
            if hasattr(klass, IS_STRAWBERRY_INTERFACE)
        ]

    graphql_type = TypeClass(
        name,
        lambda types_replacement_map=None: _get_fields(wrapped, types_replacement_map),
        **extra_kwargs
    )
    register_type(cls, graphql_type)

    return wrapped