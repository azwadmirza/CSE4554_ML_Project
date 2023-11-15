def print_conda_exception(exception):
    from conda.base.context import context

    stdoutlogger = getLogger('stdout')
    stderrlogger = getLogger('stderr')
    if context.json:
        import json
        stdoutlogger.info(json.dumps(exception.dump_map(), indent=2, sort_keys=True,
                                     cls=EntityEncoder))
    else:
        stderrlogger.info("\n\n%r", exception)