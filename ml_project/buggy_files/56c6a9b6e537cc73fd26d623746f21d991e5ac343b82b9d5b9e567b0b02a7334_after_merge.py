def fill_descriptor_types_for_related_field(ctx: FunctionContext, django_context: DjangoContext) -> MypyType:
    current_field = _get_current_field_from_assignment(ctx, django_context)
    if current_field is None:
        return AnyType(TypeOfAny.from_error)

    assert isinstance(current_field, RelatedField)

    related_model_cls = django_context.get_field_related_model_cls(current_field)
    if related_model_cls is None:
        return AnyType(TypeOfAny.from_error)

    default_related_field_type = set_descriptor_types_for_field(ctx)

    # self reference with abstract=True on the model where ForeignKey is defined
    current_model_cls = current_field.model
    if (current_model_cls._meta.abstract
            and current_model_cls == related_model_cls):
        # for all derived non-abstract classes, set variable with this name to
        # __get__/__set__ of ForeignKey of derived model
        for model_cls in django_context.all_registered_model_classes:
            if issubclass(model_cls, current_model_cls) and not model_cls._meta.abstract:
                derived_model_info = helpers.lookup_class_typeinfo(helpers.get_typechecker_api(ctx), model_cls)
                if derived_model_info is not None:
                    fk_ref_type = Instance(derived_model_info, [])
                    derived_fk_type = reparametrize_related_field_type(default_related_field_type,
                                                                       set_type=fk_ref_type, get_type=fk_ref_type)
                    helpers.add_new_sym_for_info(derived_model_info,
                                                 name=current_field.name,
                                                 sym_type=derived_fk_type)

    related_model = related_model_cls
    related_model_to_set = related_model_cls
    if related_model_to_set._meta.proxy_for_model is not None:
        related_model_to_set = related_model_to_set._meta.proxy_for_model

    typechecker_api = helpers.get_typechecker_api(ctx)

    related_model_info = helpers.lookup_class_typeinfo(typechecker_api, related_model)
    if related_model_info is None:
        # maybe no type stub
        related_model_type = AnyType(TypeOfAny.unannotated)
    else:
        related_model_type = Instance(related_model_info, [])  # type: ignore

    related_model_to_set_info = helpers.lookup_class_typeinfo(typechecker_api, related_model_to_set)
    if related_model_to_set_info is None:
        # maybe no type stub
        related_model_to_set_type = AnyType(TypeOfAny.unannotated)
    else:
        related_model_to_set_type = Instance(related_model_to_set_info, [])  # type: ignore

    # replace Any with referred_to_type
    return reparametrize_related_field_type(default_related_field_type,
                                            set_type=related_model_to_set_type,
                                            get_type=related_model_type)