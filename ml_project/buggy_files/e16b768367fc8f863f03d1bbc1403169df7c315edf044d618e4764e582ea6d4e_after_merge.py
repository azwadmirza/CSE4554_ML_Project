def compile_Shape(
        shape: qlast.Shape, *, ctx: context.ContextLevel) -> irast.Set:
    expr = setgen.ensure_set(dispatch.compile(shape.expr, ctx=ctx), ctx=ctx)
    expr_stype = setgen.get_set_type(expr, ctx=ctx)
    if not isinstance(expr_stype, s_objtypes.ObjectType):
        raise errors.QueryError(
            f'shapes cannot be applied to '
            f'{expr_stype.get_verbosename(ctx.env.schema)}',
            context=shape.context,
        )
    view_type = viewgen.process_view(
        stype=expr_stype, path_id=expr.path_id,
        elements=shape.elements, parser_context=shape.context, ctx=ctx)

    return setgen.ensure_set(expr, type_override=view_type, ctx=ctx)