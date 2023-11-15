    def __init__(self, shell, arguments=None):
        self.shell = shell
        self._raw_arguments = arguments

        if shell == 'posix':
            self.pathsep_join = ':'.join
            self.path_conversion = native_path_to_unix
            self.script_extension = '.sh'
            self.tempfile_extension = None  # write instructions to stdout rather than a temp file
            self.shift_args = 0
            self.command_join = '\n'

            self.unset_var_tmpl = 'unset %s'
            self.export_var_tmpl = "export %s='%s'"
            self.set_var_tmpl = "%s='%s'"
            self.run_script_tmpl = '. "%s"'

        elif shell == 'csh':
            self.pathsep_join = ':'.join
            self.path_conversion = native_path_to_unix
            self.script_extension = '.csh'
            self.tempfile_extension = None  # write instructions to stdout rather than a temp file
            self.shift_args = 0
            self.command_join = ';\n'

            self.unset_var_tmpl = 'unset %s'
            self.export_var_tmpl = 'setenv %s "%s"'
            self.set_var_tmpl = "set %s='%s'"
            self.run_script_tmpl = 'source "%s"'

        elif shell == 'xonsh':
            self.pathsep_join = ':'.join
            self.path_conversion = native_path_to_unix
            self.script_extension = '.xsh'
            self.tempfile_extension = '.xsh'
            self.shift_args = 0
            self.command_join = '\n'

            self.unset_var_tmpl = 'del $%s'
            self.export_var_tmpl = "$%s = '%s'"
            self.run_script_tmpl = 'source "%s"'

        elif shell == 'cmd.exe':
            self.pathsep_join = ';'.join
            self.path_conversion = path_identity
            self.script_extension = '.bat'
            self.tempfile_extension = '.bat'
            self.shift_args = 1
            self.command_join = '\n'

            self.unset_var_tmpl = '@SET %s='
            self.export_var_tmpl = '@SET "%s=%s"'
            self.run_script_tmpl = '@CALL "%s"'

        elif shell == 'fish':
            self.pathsep_join = '" "'.join
            self.path_conversion = native_path_to_unix
            self.script_extension = '.fish'
            self.tempfile_extension = None  # write instructions to stdout rather than a temp file
            self.shift_args = 0
            self.command_join = ';\n'

            self.unset_var_tmpl = 'set -e %s'
            self.export_var_tmpl = 'set -gx %s "%s"'
            self.run_script_tmpl = 'source "%s"'

        elif shell == 'powershell':
            self.pathsep_join = ';'.join
            self.path_conversion = path_identity
            self.script_extension = '.ps1'
            self.tempfile_extension = None  # write instructions to stdout rather than a temp file
            self.shift_args = 0
            self.command_join = '\n'

            self.unset_var_tmpl = 'Remove-Variable %s'
            self.export_var_tmpl = '$env:%s = "%s"'
            self.run_script_tmpl = '. "%s"'

        else:
            raise NotImplementedError()