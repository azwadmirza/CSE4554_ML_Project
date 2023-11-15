def print_unexpected_error_message(e):
    # bomb = "\U0001F4A3 "
    # explosion = "\U0001F4A5 "
    # fire = "\U0001F525 "
    # print("%s  %s  %s" % (3*bomb, 3*explosion, 3*fire))
    traceback = format_exc()

    stderrlogger = getLogger('stderr')

    from .base.context import context
    if context.json:
        from .cli.common import stdout_json
        stdout_json(dict(error=traceback))
    else:
        message = """\
An unexpected error has occurred.
Please consider posting the following information to the
conda GitHub issue tracker at:

    https://github.com/conda/conda/issues

"""
        stderrlogger.info(message)
        command = ' '.join(sys.argv)
        if ' info' not in command:
            from .cli.main_info import get_info_dict, get_main_info_str
            stderrlogger.info(get_main_info_str(get_info_dict()))
        stderrlogger.info("`$ {0}`".format(command))
        stderrlogger.info('\n')
        stderrlogger.info('\n'.join('    ' + line for line in traceback.splitlines()))