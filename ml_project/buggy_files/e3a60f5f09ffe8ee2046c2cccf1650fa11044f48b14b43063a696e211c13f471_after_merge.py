def check_output_runner(cmd, stderr=None):
    # Used to run several utilities, like Pacman detect, AIX version, uname, SCM
    tmp_file = tempfile.mktemp()
    try:
        # We don't want stderr to print warnings that will mess the pristine outputs
        stderr = stderr or subprocess.PIPE
        cmd = cmd if isinstance(cmd, six.string_types) else subprocess.list2cmdline(cmd)
        command = '{} > "{}"'.format(cmd, tmp_file)
        logger.info("Calling command: {}".format(command))
        process = subprocess.Popen(command, shell=True, stderr=stderr)
        stdout, stderr = process.communicate()
        logger.info("Return code: {}".format(int(process.returncode)))

        if process.returncode:
            # Only in case of error, we print also the stderr to know what happened
            raise CalledProcessErrorWithStderr(process.returncode, cmd, output=stderr)

        output = load(tmp_file)
        try:
            logger.info("Output: in file:{}\nstdout: {}\nstderr:{}".format(output, stdout, stderr))
        except Exception as exc:
            logger.error("Error logging command output: {}".format(exc))
        return output
    finally:
        try:
            os.unlink(tmp_file)
        except OSError:
            pass