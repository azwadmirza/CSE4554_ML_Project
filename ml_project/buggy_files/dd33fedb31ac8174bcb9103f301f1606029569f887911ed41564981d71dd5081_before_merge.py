def check_should_enable_pagination(input_tokens, parsed_args, parsed_globals,
                                   **kwargs):
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