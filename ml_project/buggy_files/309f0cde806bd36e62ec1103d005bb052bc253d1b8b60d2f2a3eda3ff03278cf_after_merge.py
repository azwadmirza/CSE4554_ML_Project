    def files_in_archive(self, force_refresh=False):
        if self._files_in_archive and not force_refresh:
            return self._files_in_archive

        cmd = [self.cmd_path, '--list', '-C', self.b_dest]
        if self.zipflag:
            cmd.append(self.zipflag)
        if self.opts:
            cmd.extend(['--show-transformed-names'] + self.opts)
        if self.excludes:
            cmd.extend(['--exclude=' + f for f in self.excludes])
        cmd.extend(['-f', self.src])
        rc, out, err = self.module.run_command(cmd, cwd=self.b_dest, environ_update=dict(LANG='C', LC_ALL='C', LC_MESSAGES='C'))

        if rc != 0:
            raise UnarchiveError('Unable to list files in the archive')

        for filename in out.splitlines():
            # Compensate for locale-related problems in gtar output (octal unicode representation) #11348
            # filename = filename.decode('string_escape')
            filename = to_native(codecs.escape_decode(filename)[0])

            # We don't allow absolute filenames.  If the user wants to unarchive rooted in "/"
            # they need to use "dest: '/'".  This follows the defaults for gtar, pax, etc.
            # Allowing absolute filenames here also causes bugs: https://github.com/ansible/ansible/issues/21397
            if filename.startswith('/'):
                filename = filename[1:]

            exclude_flag = False
            if self.excludes:
                for exclude in self.excludes:
                    if fnmatch.fnmatch(filename, exclude):
                        exclude_flag = True
                        break

            if not exclude_flag:
                self._files_in_archive.append(to_native(filename))

        return self._files_in_archive