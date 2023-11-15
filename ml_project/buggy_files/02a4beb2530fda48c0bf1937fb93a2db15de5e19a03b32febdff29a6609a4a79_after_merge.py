    def add_cache_arguments(_, **kwargs):  # pylint: disable=unused-argument

        command_table = kwargs.get('commands_loader').command_table

        if not command_table:
            return

        class CacheAction(argparse.Action):  # pylint:disable=too-few-public-methods

            def __call__(self, parser, namespace, values, option_string=None):
                setattr(namespace, cache_dest, True)
                # save caching status to CLI context
                cmd = getattr(namespace, 'cmd', None) or getattr(namespace, '_cmd', None)
                cmd.cli_ctx.data[cache_dest] = True

        for command in command_table.values():
            supports_local_cache = command.command_kwargs.get('supports_local_cache')
            if supports_local_cache:
                command.arguments[cache_dest] = CLICommandArgument(
                    '_cache',
                    options_list='--defer',
                    nargs='?',
                    action=CacheAction,
                    help='Temporarily store the object in the local cache instead of sending to Azure. '
                         'Use `az cache` commands to view/clear.'
                )