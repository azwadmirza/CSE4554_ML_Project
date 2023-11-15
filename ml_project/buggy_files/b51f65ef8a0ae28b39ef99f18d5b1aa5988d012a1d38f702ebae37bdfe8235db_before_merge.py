    def shim_cmd(self, cmd_str, extension='py'):
        '''
        Run a shim command.

        If tty is enabled, we must scp the shim to the target system and
        execute it there
        '''
        if not self.tty and not self.winrm:
            return self.shell.exec_cmd(cmd_str)

        # Write the shim to a temporary file in the default temp directory
        with tempfile.NamedTemporaryFile(mode='w+b',
                                         prefix='shim_',
                                         delete=False) as shim_tmp_file:
            shim_tmp_file.write(cmd_str)

        # Copy shim to target system, under $HOME/.<randomized name>
        target_shim_file = '.{0}.{1}'.format(binascii.hexlify(os.urandom(6)), extension)
        if self.winrm:
            target_shim_file = saltwinshell.get_target_shim_file(self)
        self.shell.send(shim_tmp_file.name, target_shim_file, makedirs=True)

        # Remove our shim file
        try:
            os.remove(shim_tmp_file.name)
        except IOError:
            pass

        # Execute shim
        if extension == 'ps1':
            ret = self.shell.exec_cmd('"powershell {0}"'.format(target_shim_file))
        else:
            if not self.winrm:
                ret = self.shell.exec_cmd('/bin/sh \'$HOME/{0}\''.format(target_shim_file))
            else:
                ret = saltwinshell.call_python(self)

        # Remove shim from target system
        if not self.winrm:
            self.shell.exec_cmd('rm \'$HOME/{0}\''.format(target_shim_file))
        else:
            self.shell.exec_cmd('del {0}'.format(target_shim_file))

        return ret