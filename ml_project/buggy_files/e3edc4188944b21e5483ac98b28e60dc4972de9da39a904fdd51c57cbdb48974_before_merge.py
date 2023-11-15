def run_commands(module, commands, check_rc=True):
    responses = list()

    for cmd in to_list(commands):
        rc, out, err = exec_command(module, cmd)
        if check_rc and rc != 0:
            module.fail_json(msg=err, rc=rc)
        responses.append(out)
    return responses