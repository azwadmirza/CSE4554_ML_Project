    def _exec(self, args):
        cmd = [self._icinga2, 'feature']
        rc, out, err = self.module.run_command(cmd + args, check_rc=True)
        return rc, out