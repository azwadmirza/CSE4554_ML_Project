def load_config(module, commands):
    rc, out, err = exec_command(module, 'configure terminal')
    if rc != 0:
        module.fail_json(msg='unable to enter configuration mode', err=to_text(err, errors='surrogate_or_strict'))

    for command in to_list(commands):
        if command == 'end':
            continue
#        cmd = {'command': command, 'prompt': WARNING_PROMPTS_RE, 'answer': 'yes'}
        rc, out, err = exec_command(module, command)
        if rc != 0:
            module.fail_json(msg=to_text(err, errors='surrogate_or_strict'), command=command, rc=rc)
    exec_command(module, 'end')