def execute_show_command(command, module):
    if module.params['transport'] == 'cli':
        command += ' | json'
    cmds = [command]
    body = run_commands(module, cmds)
    return body