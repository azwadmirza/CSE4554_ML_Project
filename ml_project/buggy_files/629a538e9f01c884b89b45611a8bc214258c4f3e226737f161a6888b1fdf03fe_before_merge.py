    def reload_sysctl(self):
        # do it
        if self.platform == 'freebsd':
            # freebsd doesn't support -p, so reload the sysctl service
            rc, out, err = self.module.run_command('/etc/rc.d/sysctl reload', environ_update=self.LANG_ENV)
        elif self.platform == 'openbsd':
            # openbsd doesn't support -p and doesn't have a sysctl service,
            # so we have to set every value with its own sysctl call
            for k, v in self.file_values.items():
                rc = 0
                if k != self.args['name']:
                    rc = self.set_token_value(k, v)
                    if rc != 0:
                        break
            if rc == 0 and self.args['state'] == "present":
                rc = self.set_token_value(self.args['name'], self.args['value'])
        else:
            # system supports reloading via the -p flag to sysctl, so we'll use that
            sysctl_args = [self.sysctl_cmd, '-p', self.sysctl_file]
            if self.args['ignoreerrors']:
                sysctl_args.insert(1, '-e')

            rc, out, err = self.module.run_command(sysctl_args, environ_update=self.LANG_ENV)

        if rc != 0 or self._stderr_failed(err):
            self.module.fail_json(msg="Failed to reload sysctl: %s" % to_native(out) + to_native(err))