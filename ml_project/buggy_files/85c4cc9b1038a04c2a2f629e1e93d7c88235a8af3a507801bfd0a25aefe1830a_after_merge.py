    def cmd_block(self, is_retry=False):
        '''
        Prepare the precheck command to send to the subsystem
        '''
        # 1. check if python is on the target
        # 2. check is salt-call is on the target
        # 3. deploy salt-thin
        # 4. execute command
        sudo = 'sudo' if self.target['sudo'] else ''
        cmd = SSH_SHIM.format(sudo, self.arg_str)
        log.debug("Performing shimmed command as follows:\n{0}".format(cmd))
        stdout, stderr = self.shell.exec_cmd(cmd)

        log.debug("STDOUT {1}\n{0}".format(stdout, self.target['host']))
        log.debug("STDERR {1}\n{0}".format(stderr, self.target['host']))

        error = self.categorize_shim_errors(stdout, stderr)
        if error:
            return "ERROR: {0}".format(error), stderr

        if RSTR in stdout:
            stdout = stdout.split(RSTR)[1].strip()

        return stdout, stderr