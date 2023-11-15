    def run(self):
        '''Set up subprocess and execute command

        :param cmd_input: input to pass to command in STDIN
        :type cmd_input: str
        :param combine_output: combine STDERR into STDOUT
        '''
        log.info("Running: '%s' [%s]", self.get_command(), self.cwd)

        stdout = subprocess.PIPE
        stderr = subprocess.PIPE
        stdin = None
        if self.input_data is not None:
            stdin = subprocess.PIPE
        if self.combine_output:
            stderr = subprocess.STDOUT

        environment = {}
        environment.update(self.environment)
        environment['READTHEDOCS'] = 'True'
        if 'DJANGO_SETTINGS_MODULE' in environment:
            del environment['DJANGO_SETTINGS_MODULE']
        if 'PYTHONPATH' in environment:
            del environment['PYTHONPATH']

        try:
            proc = subprocess.Popen(
                self.command,
                shell=self.shell,
                cwd=self.cwd,
                stdin=stdin,
                stdout=stdout,
                stderr=stderr,
                env=environment,
            )
            cmd_input = None
            if self.input_data is not None:
                cmd_input = self.input_data

            cmd_output = proc.communicate(input=cmd_input)
            (cmd_stdout, cmd_stderr) = cmd_output
            try:
                self.output = cmd_stdout.decode('utf-8', 'replace')
            except (TypeError, AttributeError):
                self.output = None
            try:
                self.error = cmd_stderr.decode('utf-8', 'replace')
            except (TypeError, AttributeError):
                self.error = None
            self.status = proc.returncode
        except OSError:
            self.error = traceback.format_exc()
            self.output = self.error
            self.status = -1