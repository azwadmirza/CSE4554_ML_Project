    def unarchive(self):
        cmd = [self.cmd_path, '--extract', '-C', self.dest]
        if self.zipflag:
            cmd.append(self.zipflag)
        if self.opts:
            cmd.extend(['--show-transformed-names'] + self.opts)
        if self.file_args['owner']:
            cmd.append('--owner=' + quote(self.file_args['owner']))
        if self.file_args['group']:
            cmd.append('--group=' + quote(self.file_args['group']))
        if self.module.params['keep_newer']:
            cmd.append('--keep-newer-files')
        if self.excludes:
            cmd.extend(['--exclude=' + f for f in self.excludes])
        cmd.extend(['-f', self.src])
        rc, out, err = self.module.run_command(cmd, cwd=self.dest, environ_update=dict(LANG='C', LC_ALL='C', LC_MESSAGES='C'))
        return dict(cmd=cmd, rc=rc, out=out, err=err)