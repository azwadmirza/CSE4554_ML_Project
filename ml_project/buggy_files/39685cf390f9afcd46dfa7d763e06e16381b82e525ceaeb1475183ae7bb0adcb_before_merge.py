def create_script(command):
    """Write out a script onto a target.

    This method should be backward compatible with Python 2.4+ when executing
    from within the container.

    :param command: command to run, this can be a script and can use spacing
                    with newlines as separation.
    :type command: ``str``
    """

    (fd, script_file) = tempfile.mkstemp(prefix='lxc-attach-script')
    f = os.fdopen(fd, 'wb')
    try:
        f.write(ATTACH_TEMPLATE % {'container_command': command})
        f.flush()
    finally:
        f.close()

    # Ensure the script is executable.
    os.chmod(script_file, int('0700',8))

    # Output log file.
    stdout_file = os.fdopen(tempfile.mkstemp(prefix='lxc-attach-script-log')[0], 'ab')

    # Error log file.
    stderr_file = os.fdopen(tempfile.mkstemp(prefix='lxc-attach-script-err')[0], 'ab')

    # Execute the script command.
    try:
        subprocess.Popen(
            [script_file],
            stdout=stdout_file,
            stderr=stderr_file
        ).communicate()
    finally:
        # Close the log files.
        stderr_file.close()
        stdout_file.close()

        # Remove the script file upon completion of execution.
        os.remove(script_file)