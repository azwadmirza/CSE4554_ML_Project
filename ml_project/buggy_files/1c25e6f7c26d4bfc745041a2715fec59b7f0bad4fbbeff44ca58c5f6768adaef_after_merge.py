    def unarchive(self):
        cmd = [self.cmd_path, '-o']
        if self.opts:
            cmd.extend(self.opts)
        cmd.append(self.src)
        # NOTE: Including (changed) files as arguments is problematic (limits on command line/arguments)
        # if self.includes:
        # NOTE: Command unzip has this strange behaviour where it expects quoted filenames to also be escaped
        # cmd.extend(map(shell_escape, self.includes))
        if self.excludes:
            cmd.extend(['-x'] + self.excludes)
        cmd.extend(['-d', self.b_dest])
        rc, out, err = self.module.run_command(cmd)
        return dict(cmd=cmd, rc=rc, out=out, err=err)