def _flatpak_command(module, noop, command):
    global result
    if noop:
        result['rc'] = 0
        result['command'] = command
        return ""

    process = subprocess.Popen(
        command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_data, stderr_data = process.communicate()
    result['rc'] = process.returncode
    result['command'] = command
    result['stdout'] = stdout_data
    result['stderr'] = stderr_data
    if result['rc'] != 0:
        module.fail_json(msg="Failed to execute flatpak command", **result)
    return to_native(stdout_data)