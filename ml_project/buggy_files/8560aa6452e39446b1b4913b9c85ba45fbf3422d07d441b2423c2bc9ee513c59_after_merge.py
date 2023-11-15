    def run(self, deploy_attempted=False):
        '''
        Execute the routine, the routine can be either:
        1. Execute a raw shell command
        2. Execute a wrapper func
        3. Execute a remote Salt command

        If a (re)deploy is needed, then retry the operation after a deploy
        attempt

        Returns tuple of (stdout, stderr)
        '''

        stdout, stderr = None, None

        if self.opts.get('raw_shell'):
            stdout, stderr = self.shell.exec_cmd(self.arg_str)

        elif self.fun in self.wfuncs:
            stdout, stderr = self.run_wfunc()

        else:
            stdout, stderr = self.cmd_block()

        if stdout.startswith('deploy') and not deploy_attempted:
            self.deploy()
            return self.run(deploy_attempted=True)

        return stdout, stderr