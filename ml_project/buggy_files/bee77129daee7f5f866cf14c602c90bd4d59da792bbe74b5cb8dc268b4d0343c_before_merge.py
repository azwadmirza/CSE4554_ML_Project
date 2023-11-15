def register_cache_arguments(cli_ctx):
    from knack import events
    from azure.cli.core.commands.parameters import CaseInsensitiveList

    cache_dest = '_cache'

    def add_cache_arguments(_, **kwargs):  # pylint: disable=unused-argument

        command_table = kwargs.get('commands_loader').command_table

        if not command_table:
            return

        class CacheAction(argparse.Action):  # pylint:disable=too-few-public-methods

            def __call__(self, parser, namespace, values, option_string=None):
                setattr(namespace, cache_dest, values)
                # save caching status to CLI context
                cmd = getattr(namespace, 'cmd', None) or getattr(namespace, '_cmd', None)
                cmd.cli_ctx.data[cache_dest] = values

        for command in command_table.values():
            supports_local_cache = command.command_kwargs.get('supports_local_cache')
            if supports_local_cache:
                command.arguments[cache_dest] = CLICommandArgument(
                    '_cache',
                    options_list='--cache',
                    arg_group='Caching Strategy',
                    nargs='+',
                    choices=CaseInsensitiveList(['read', 'write', 'write-through']),
                    action=CacheAction,
                    help='Space-separated list of caching directives.'
                )

    cli_ctx.register_event(events.EVENT_INVOKER_POST_CMD_TBL_CREATE, add_cache_arguments)