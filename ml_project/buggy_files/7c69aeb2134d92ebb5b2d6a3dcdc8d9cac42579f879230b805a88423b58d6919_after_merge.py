def rollback(filename, module):
    commands = ['rollback running-config file %s' % filename]
    run_commands(module, commands)