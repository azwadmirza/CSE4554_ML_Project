            def __call__(self, parser, namespace, values, option_string=None):
                setattr(namespace, cache_dest, True)
                # save caching status to CLI context
                cmd = getattr(namespace, 'cmd', None) or getattr(namespace, '_cmd', None)
                cmd.cli_ctx.data[cache_dest] = True