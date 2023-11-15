def get_path_serialized_output(
        rel: pgast.Query, path_id: irast.PathId, *,
        env: context.Environment) -> pgast.OutputVar:
    # Serialized output is a special case, we don't
    # want this behaviour to be recursive, so it
    # must be kept outside of get_path_output() generic.
    aspect = 'serialized'

    result = rel.path_outputs.get((path_id, aspect))
    if result is not None:
        return result

    ref = get_path_serialized_or_value_var(rel, path_id, env=env)

    refexpr = output.serialize_expr(ref, path_id=path_id, env=env)
    alias = get_path_output_alias(path_id, aspect, env=env)

    restarget = pgast.ResTarget(name=alias, val=refexpr, ser_safe=True)
    rel.target_list.append(restarget)

    result = pgast.ColumnRef(
        name=[alias], nullable=refexpr.nullable, ser_safe=True)

    _put_path_output_var(rel, path_id, aspect, result, env=env)

    return result