    def cmd_block(self):
        '''
        Prepare the precheck command to send to the subsystem
        '''
        # 1. check if python is on the target
        # 2. check is salt-call is on the target
        # 3. deploy salt-thin
        # 4. execute command
        sudo = 'sudo' if self.target['sudo'] else ''
        cmd = SSH_SHIM.format(sudo, self.arg_str)
        stdout, stderr = self.shell.exec_cmd(cmd)
        if RSTR in stdout:
            stdout = stdout.split(RSTR)[1].strip()
        if stdout.startswith('deploy'):
            self.deploy()
            stdout, stderr = self.shell.exec_cmd(cmd)
            if RSTR in stdout:
                stdout = stdout.split(RSTR)[1].strip()
        return stdout, stderr