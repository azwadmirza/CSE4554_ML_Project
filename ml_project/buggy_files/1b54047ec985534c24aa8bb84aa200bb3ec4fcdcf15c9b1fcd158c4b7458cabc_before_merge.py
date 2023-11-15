    def _default_target_from_env(self):
        '''Set and return the default CrayPE target loaded in a clean login
        session.

        A bash subshell is launched with a wiped environment and the list of
        loaded modules is parsed for the first acceptable CrayPE target.
        '''
        # env -i /bin/bash -lc echo $CRAY_CPU_TARGET 2> /dev/null
        if getattr(self, 'default', None) is None:
            output = Executable('/bin/bash')('-lc', 'echo $CRAY_CPU_TARGET',
                                             env={'TERM': os.environ['TERM']},
                                             output=str, error=os.devnull)
            output = ''.join(output.split())  # remove all whitespace
            if output:
                self.default = output
                tty.debug("Found default module:%s" % self.default)
        return self.default