def checkpoint(filename, module):
    commands = ['terminal dont-ask', 'checkpoint file %s' % filename]
    run_commands(module, commands)