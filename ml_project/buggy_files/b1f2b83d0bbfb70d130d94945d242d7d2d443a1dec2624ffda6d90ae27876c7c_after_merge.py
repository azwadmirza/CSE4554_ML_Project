def get_choices(cli, prog_name, args, incomplete):
    """
    :param cli: command definition
    :param prog_name: the program that is running
    :param args: full list of args
    :param incomplete: the incomplete text to autocomplete
    :return: all the possible completions for the incomplete
    """
    all_args = copy.deepcopy(args)

    ctx = resolve_ctx(cli, prog_name, args)
    if ctx is None:
        return []

    # In newer versions of bash long opts with '='s are partitioned, but it's easier to parse
    # without the '='
    if start_of_option(incomplete) and WORDBREAK in incomplete:
        partition_incomplete = incomplete.partition(WORDBREAK)
        all_args.append(partition_incomplete[0])
        incomplete = partition_incomplete[2]
    elif incomplete == WORDBREAK:
        incomplete = ''

    completions = []
    if start_of_option(incomplete):
        # completions for partial options
        for param in ctx.command.params:
            if isinstance(param, Option):
                param_opts = [param_opt for param_opt in param.opts +
                              param.secondary_opts if param_opt not in all_args or param.multiple]
                completions.extend(
                    [(o, param.help) for o in param_opts if o.startswith(incomplete)])
        return completions
    # completion for option values from user supplied values
    for param in ctx.command.params:
        if is_incomplete_option(all_args, param):
            return get_user_autocompletions(ctx, all_args, incomplete, param)
    # completion for argument values from user supplied values
    for param in ctx.command.params:
        if is_incomplete_argument(ctx.params, param):
            return get_user_autocompletions(ctx, all_args, incomplete, param)

    add_subcommand_completions(ctx, incomplete, completions)
    return completions