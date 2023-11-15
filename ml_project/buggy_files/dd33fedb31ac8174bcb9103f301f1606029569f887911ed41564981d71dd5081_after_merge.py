def check_should_enable_pagination(input_tokens, shadowed_args, argument_table,
                                   parsed_args, parsed_globals, **kwargs):
    normalized_paging_args = ['start_token', 'max_items']
    for token in input_tokens:
        py_name = token.replace('-', '_')
        if getattr(parsed_args, py_name) is not None and \
                py_name not in normalized_paging_args:
            # The user has specified a manual (undocumented) pagination arg.
            # We need to automatically turn pagination off.
            logger.debug("User has specified a manual pagination arg. "
                         "Automatically setting --no-paginate.")
            parsed_globals.paginate = False
            # Because we've now disabled pagination, there's a chance that
            # we were shadowing arguments.  For example, we inject a
            # --max-items argument in unify_paging_params().  If the
            # the operation also provides its own MaxItems (which we
            # expose as --max-items) then our custom pagination arg
            # was shadowing the customers arg.  When we turn pagination
            # off we need to put back the original argument which is
            # what we're doing here.
            for key, value in shadowed_args.items():
                argument_table[key] = value