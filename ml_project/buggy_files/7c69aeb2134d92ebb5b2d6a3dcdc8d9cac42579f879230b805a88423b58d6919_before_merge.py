def rollback(filename, module):
    commands = ['rollback running-config file %s' % filename]
    try:
        module.configure(commands)
    except AttributeError:
        try:
            module.cli.add_commands(commands, output='config')
            module.cli.run_commands()
        except ShellError:
            clie = get_exception()
            module.fail_json(msg='Error sending CLI commands',
                             error=str(clie), commands=commands)