def compile_Set(
        ir_set: irast.Set, *,
        ctx: context.CompilerContextLevel) -> pgast.BaseExpr:

    if ctx.singleton_mode:
        return _compile_set_in_singleton_mode(ir_set, ctx=ctx)

    is_toplevel = ctx.toplevel_stmt is context.NO_STMT

    _compile_set_impl(ir_set, ctx=ctx)

    if is_toplevel:
        if isinstance(ir_set.expr, irast.ConfigCommand):
            return config.top_output_as_config_op(
                ir_set, ctx.rel, env=ctx.env)
        else:
            return output.top_output_as_value(ctx.rel, ir_set, env=ctx.env)
    else:
        value = pathctx.get_path_value_var(
            ctx.rel, ir_set.path_id, env=ctx.env)

        return output.output_as_value(value, env=ctx.env)