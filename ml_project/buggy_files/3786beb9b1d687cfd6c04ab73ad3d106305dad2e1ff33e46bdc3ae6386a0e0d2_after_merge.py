    def pip_install_deps(requirements_path):
        """Pip install a requirements.txt file and wait for finish."""
        process = None
        command = ["pip", "install",
                   "--target={}".format(DEFAULT_MODULE_DEPS_PATH),
                   "--ignore-installed", "-r", requirements_path]

        try:
            process = subprocess.Popen(command,
                                       shell=False,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)

        except FileNotFoundError:
            _LOGGER.debug("Couldn't find the command 'pip', "
                          "trying again with command 'pip3'")

        try:
            command[0] = "pip3"
            process = subprocess.Popen(command,
                                       shell=False,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        except FileNotFoundError:
            _LOGGER.debug("Couldn't find the command 'pip3', "
                          "install of %s will be skipped.",
                          str(requirements_path))

        if not process:
            raise OSError("Pip and pip3 not found, exiting...")

        for output in process.communicate():
            if output != "":
                for line in output.splitlines():
                    _LOGGER.debug(str(line).strip())

        process.wait()
        return True