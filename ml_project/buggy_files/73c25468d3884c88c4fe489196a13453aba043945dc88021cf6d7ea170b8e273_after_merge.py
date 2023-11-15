def get_expr_referrers(schema: s_schema.Schema,
                       obj: so.Object) -> Dict[so.Object, List[str]]:
    """Return schema referrers with refs in expressions."""

    refs: Dict[Tuple[Type[so.Object], str], FrozenSet[so.Object]] = (
        schema.get_referrers_ex(obj))
    result: Dict[so.Object, List[str]] = {}

    for (mcls, fn), referrers in refs.items():
        field = mcls.get_field(fn)
        if issubclass(field.type, (Expression, ExpressionList)):
            for ref in referrers:
                result.setdefault(ref, []).append(fn)

    return result