    def write(self, backup_file=None):
        """
        Write the crontab to the system. Saves all information.
        """
        if backup_file:
            fileh = open(backup_file, 'wb')
        elif self.cron_file:
            fileh = open(self.b_cron_file, 'wb')
        else:
            filed, path = tempfile.mkstemp(prefix='crontab')
            os.chmod(path, int('0644', 8))
            fileh = os.fdopen(filed, 'wb')

        fileh.write(to_bytes(self.render()))
        fileh.close()

        # return if making a backup
        if backup_file:
            return

        # Add the entire crontab back to the user crontab
        if not self.cron_file:
            # quoting shell args for now but really this should be two non-shell calls.  FIXME
            (rc, out, err) = self.module.run_command(self._write_execute(path), use_unsafe_shell=True)
            os.unlink(path)

            if rc != 0:
                self.module.fail_json(msg=err)

        # set SELinux permissions
        if self.module.selinux_enabled() and self.cron_file:
            self.module.set_default_selinux_context(self.cron_file, False)