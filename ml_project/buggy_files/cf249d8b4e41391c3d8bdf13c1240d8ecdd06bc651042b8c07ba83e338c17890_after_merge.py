def get_field_type_from_lookup(ctx: MethodContext, django_context: DjangoContext, model_cls: Type[Model],
                               *, method: str, lookup: str) -> Optional[MypyType]:
    try:
        lookup_field = django_context.resolve_lookup_into_field(model_cls, lookup)
    except FieldError as exc:
        ctx.api.fail(exc.args[0], ctx.context)
        return None
    except LookupsAreUnsupported:
        return AnyType(TypeOfAny.explicit)

    if ((isinstance(lookup_field, RelatedField) and lookup_field.column == lookup)
            or isinstance(lookup_field, ForeignObjectRel)):
        related_model_cls = django_context.get_field_related_model_cls(lookup_field)
        if related_model_cls is None:
            return AnyType(TypeOfAny.from_error)
        lookup_field = django_context.get_primary_key_field(related_model_cls)

    field_get_type = django_context.get_field_get_type(helpers.get_typechecker_api(ctx),
                                                       lookup_field, method=method)
    return field_get_type