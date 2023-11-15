def resolve_ctx(cli, prog_name, args):
    """
    Parse into a hierarchy of contexts. Contexts are connected through the parent variable.
    :param cli: command definition
    :param prog_name: the program that is running
    :param args: full list of args
    :return: the final context/command parsed
    """
    ctx = cli.make_context(prog_name, args, resilient_parsing=True)
    args = ctx.protected_args + ctx.args
    while args:
        if isinstance(ctx.command, MultiCommand):
            if not ctx.command.chain:
                cmd_name, cmd, args = ctx.command.resolve_command(ctx, args)
                if cmd is None:
                    return ctx
                ctx = cmd.make_context(cmd_name, args, parent=ctx,
                                       resilient_parsing=True)
                args = ctx.protected_args + ctx.args
            else:
                # Walk chained subcommand contexts saving the last one.
                while args:
                    cmd_name, cmd, args = ctx.command.resolve_command(ctx, args)
                    if cmd is None:
                        return ctx
                    sub_ctx = cmd.make_context(cmd_name, args, parent=ctx,
                                               allow_extra_args=True,
                                               allow_interspersed_args=False,
                                               resilient_parsing=True)
                    args = sub_ctx.args
                ctx = sub_ctx
                args = sub_ctx.protected_args + sub_ctx.args
        else:
            break
    return ctx