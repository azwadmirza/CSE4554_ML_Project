def unify_paging_params(argument_table, operation_model, event_name,
                        session, **kwargs):

    paginator_config = get_paginator_config(
        session, operation_model.service_model.service_name,
        operation_model.name)
    if paginator_config is None:
        # We only apply these customizations to paginated responses.
        return
    logger.debug("Modifying paging parameters for operation: %s",
                 operation_model.name)
    _remove_existing_paging_arguments(argument_table, paginator_config)
    parsed_args_event = event_name.replace('building-argument-table.',
                                           'operation-args-parsed.')
    session.register(
        parsed_args_event,
        partial(check_should_enable_pagination,
                list(_get_all_cli_input_tokens(paginator_config))))
    argument_table['starting-token'] = PageArgument('starting-token',
                                                    STARTING_TOKEN_HELP,
                                                    parse_type='string')
    input_members = operation_model.input_shape.members
    type_name = 'integer'
    if 'limit_key' in paginator_config:
        limit_key_shape = input_members[paginator_config['limit_key']]
        type_name = limit_key_shape.type_name
        if type_name not in PageArgument.type_map:
            raise TypeError(
                ('Unsupported pagination type {0} for operation {1}'
                 ' and parameter {2}').format(
                    type_name, operation_model.name,
                    paginator_config['limit_key']))
        argument_table['page-size'] = PageArgument(
            'page-size', PAGE_SIZE_HELP, parse_type=type_name)

    argument_table['max-items'] = PageArgument('max-items', MAX_ITEMS_HELP,
                                               parse_type=type_name)