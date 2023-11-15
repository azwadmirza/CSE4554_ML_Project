    def _update_module_args(self, module_name, module_args, task_vars):

        # set check mode in the module arguments, if required
        if self._play_context.check_mode:
            if not self._supports_check_mode:
                raise AnsibleError("check mode is not supported for this operation")
            module_args['_ansible_check_mode'] = True
        else:
            module_args['_ansible_check_mode'] = False

        # set no log in the module arguments, if required
        module_args['_ansible_no_log'] = self._play_context.no_log or C.DEFAULT_NO_TARGET_SYSLOG

        # set debug in the module arguments, if required
        module_args['_ansible_debug'] = C.DEFAULT_DEBUG

        # let module know we are in diff mode
        module_args['_ansible_diff'] = self._play_context.diff

        # let module know our verbosity
        module_args['_ansible_verbosity'] = display.verbosity

        # give the module information about the ansible version
        module_args['_ansible_version'] = __version__

        # give the module information about its name
        module_args['_ansible_module_name'] = module_name

        # set the syslog facility to be used in the module
        module_args['_ansible_syslog_facility'] = task_vars.get('ansible_syslog_facility', C.DEFAULT_SYSLOG_FACILITY)

        # let module know about filesystems that selinux treats specially
        module_args['_ansible_selinux_special_fs'] = C.DEFAULT_SELINUX_SPECIAL_FS

        # give the module the socket for persistent connections
        module_args['_ansible_socket'] = getattr(self._connection, 'socket_path')
        if not module_args['_ansible_socket']:
            module_args['_ansible_socket'] = task_vars.get('ansible_socket')

        # make sure all commands use the designated shell executable
        module_args['_ansible_shell_executable'] = self._play_context.executable

        # make sure modules are aware if they need to keep the remote files
        module_args['_ansible_keep_remote_files'] = C.DEFAULT_KEEP_REMOTE_FILES

        # make sure all commands use the designated temporary directory if created
        module_args['_ansible_tmpdir'] = self._connection._shell.tmpdir

        # make sure the remote_tmp value is sent through in case modules needs to create their own
        try:
            module_args['_ansible_remote_tmp'] = self._connection._shell.get_option('remote_tmp')
        except KeyError:
            # here for 3rd party shell plugin compatibility in case they do not define the remote_tmp option
            module_args['_ansible_remote_tmp'] = '~/.ansible/tmp'