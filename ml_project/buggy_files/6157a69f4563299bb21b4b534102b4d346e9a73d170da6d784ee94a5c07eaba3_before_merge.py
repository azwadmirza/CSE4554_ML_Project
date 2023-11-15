def checkpoint(filename, module):
    commands = ['terminal dont-ask', 'checkpoint file %s' % filename]
    prepare_show_command(commands, module)