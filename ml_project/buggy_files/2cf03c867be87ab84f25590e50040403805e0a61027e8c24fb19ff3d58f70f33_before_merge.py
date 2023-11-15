def resolve_ctx(cli, prog_name, args):
    """
    Parse into a hierarchy of contexts. Contexts are connected through the parent variable.
    :param cli: command definition
    :param prog_name: the program that is running
    :param args: full list of args
    :return: the final context/command parsed
    """
    ctx = cli.make_context(prog_name, args, resilient_parsing=True)
    args_remaining = ctx.protected_args + ctx.args
    while ctx is not None and args_remaining:
        if isinstance(ctx.command, MultiCommand):
            cmd = ctx.command.get_command(ctx, args_remaining[0])
            if cmd is None:
                return None
            ctx = cmd.make_context(
                args_remaining[0], args_remaining[1:], parent=ctx, resilient_parsing=True)
            args_remaining = ctx.protected_args + ctx.args
        else:
            ctx = ctx.parent

    return ctx