    def _exec(self, args):
        if not self.module.check_mode:
            cmd = [self._icinga2, 'feature']
            rc, out, err = self.module.run_command(cmd + args, check_rc=True)
            return rc, out
        return 0, list()