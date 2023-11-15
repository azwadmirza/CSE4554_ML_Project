def execute_archive(profile, node, context):
    adapter = get_adapter(profile)

    node_cfg = node.get('config', {})

    source_columns = adapter.get_columns_in_table(
        profile, node_cfg.get('source_schema'), node_cfg.get('source_table'))

    if len(source_columns) == 0:
        raise RuntimeError(
            'Source table "{}"."{}" does not '
            'exist'.format(source_schema, source_table))

    dest_columns = source_columns + [
        dbt.schema.Column("valid_from", "timestamp", None),
        dbt.schema.Column("valid_to", "timestamp", None),
        dbt.schema.Column("scd_id", "text", None),
        dbt.schema.Column("dbt_updated_at", "timestamp", None)
    ]

    adapter.create_table(
        profile,
        schema=node_cfg.get('target_schema'),
        table=node_cfg.get('target_table'),
        columns=dest_columns,
        sort=node_cfg.get('updated_at'),
        dist=node_cfg.get('unique_key'))

    # TODO move this to inject_runtime_config, generate archive SQL
    # in wrap step. can't do this right now because we actually need
    # to inspect status of the schema at runtime and archive requires
    # a lot of information about the schema to generate queries.
    template_ctx = context.copy()
    template_ctx.update(node_cfg)

    select = dbt.clients.jinja.get_rendered(dbt.templates.SCDArchiveTemplate,
                                            template_ctx)

    insert_stmt = dbt.templates.ArchiveInsertTemplate().wrap(
        schema=node_cfg.get('target_schema'),
        table=node_cfg.get('target_table'),
        query=select,
        unique_key=node_cfg.get('unique_key'))

    node['wrapped_sql'] = dbt.clients.jinja.get_rendered(insert_stmt,
                                                         template_ctx)

    result = adapter.execute_model(
        profile=profile,
        model=node)

    return result