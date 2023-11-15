def root_command(command, *extra):
    '''Invoke a shell command as root or using sudo. The command is a
    list of shell command words'''
    full_cmd = []
    sudo = True
    if os.getuid() == 0:
        sudo = False
    if sudo:
        full_cmd.append('sudo')
    full_cmd.extend(command)
    for arg in extra:
        full_cmd.append(arg)
    # invoke
    logger.debug("Running command: %s", ' '.join(full_cmd))
    pipes = subprocess.Popen(full_cmd, stdout=subprocess.PIPE,  # nosec
                             stderr=subprocess.PIPE)
    result, error = pipes.communicate()  # nosec
    if error:
        logger.error("Command failed. %s", error.decode())
        raise subprocess.CalledProcessError(1, cmd=full_cmd, output=error)  # nosec
    return result