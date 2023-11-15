    def run(self, tmp=None, task_vars=None):
        ''' generates params and passes them on to the rsync module '''
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)

        original_transport = task_vars.get('ansible_connection') or self._play_context.connection
        remote_transport = False
        if original_transport != 'local':
            remote_transport = True

        try:
            delegate_to = self._task.delegate_to
        except (AttributeError, KeyError):
            delegate_to = None

        use_ssh_args = self._task.args.pop('use_ssh_args', None)

        # Parameter name needed by the ansible module
        self._task.args['_local_rsync_path'] = task_vars.get('ansible_rsync_path') or 'rsync'

        # rsync thinks that one end of the connection is localhost and the
        # other is the host we're running the task for  (Note: We use
        # ansible's delegate_to mechanism to determine which host rsync is
        # running on so localhost could be a non-controller machine if
        # delegate_to is used)
        src_host = '127.0.0.1'
        inventory_hostname = task_vars.get('inventory_hostname')
        dest_host_inventory_vars = task_vars['hostvars'].get(inventory_hostname)
        try:
            dest_host = dest_host_inventory_vars['ansible_host']
        except KeyError:
            dest_host = dest_host_inventory_vars.get('ansible_ssh_host', inventory_hostname)

        dest_is_local = dest_host in C.LOCALHOST

        # CHECK FOR NON-DEFAULT SSH PORT
        if self._task.args.get('dest_port', None) is None:
            inv_port = task_vars.get('ansible_ssh_port', None) or C.DEFAULT_REMOTE_PORT
            if inv_port is not None:
                self._task.args['dest_port'] = inv_port

        # Set use_delegate if we are going to run rsync on a delegated host
        # instead of localhost
        use_delegate = False
        if dest_host == delegate_to:
            # edge case: explicit delegate and dest_host are the same
            # so we run rsync on the remote machine targeting its localhost
            # (itself)
            dest_host = '127.0.0.1'
            use_delegate = True
        elif delegate_to is not None and remote_transport:
            # If we're delegating to a remote host then we need to use the
            # delegate_to settings
            use_delegate = True

        # Delegate to localhost as the source of the rsync unless we've been
        # told (via delegate_to) that a different host is the source of the
        # rsync
        transport_overridden = False
        if not use_delegate and remote_transport:
            # Create a connection to localhost to run rsync on
            new_stdin = self._connection._new_stdin
            new_connection = connection_loader.get('local', self._play_context, new_stdin)
            self._connection = new_connection
            transport_overridden = True
            self._override_module_replaced_vars(task_vars)

        # COMPARE DELEGATE, HOST AND TRANSPORT
        between_multiple_hosts = False
        if dest_host != src_host and remote_transport:
            # We're not copying two filesystem trees on the same host so we
            # need to correctly format the paths for rsync (like
            # user@host:path/to/tree
            between_multiple_hosts = True

        # SWITCH SRC AND DEST HOST PER MODE
        if self._task.args.get('mode', 'push') == 'pull':
            (dest_host, src_host) = (src_host, dest_host)

        # MUNGE SRC AND DEST PER REMOTE_HOST INFO
        src = self._task.args.get('src', None)
        dest = self._task.args.get('dest', None)
        if between_multiple_hosts:
            # Private key handling
            if use_delegate:
                private_key = task_vars.get('ansible_ssh_private_key_file') or self._play_context.private_key_file
            else:
                private_key = task_vars.get('ansible_ssh_private_key_file') or self._play_context.private_key_file

            if private_key is not None:
                private_key = os.path.expanduser(private_key)
                self._task.args['private_key'] = private_key

            # Src and dest rsync "path" handling
            # Determine if we need a user@
            user = None
            if boolean(self._task.args.get('set_remote_user', 'yes')):
                if use_delegate:
                    user = task_vars.get('ansible_delegated_vars', dict()).get('ansible_ssh_user', None)
                    if not user:
                        user = C.DEFAULT_REMOTE_USER

                else:
                    user = task_vars.get('ansible_ssh_user') or self._play_context.remote_user

            # use the mode to define src and dest's url
            if self._task.args.get('mode', 'push') == 'pull':
                # src is a remote path: <user>@<host>, dest is a local path
                src = self._process_remote(src_host, src, user)
                dest = self._process_origin(dest_host, dest, user)
            else:
                # src is a local path, dest is a remote path: <user>@<host>
                src = self._process_origin(src_host, src, user)
                dest = self._process_remote(dest_host, dest, user)
        else:
            # Still need to munge paths (to account for roles) even if we aren't
            # copying files between hosts
            if not src.startswith('/'):
                src = self._get_absolute_path(path=src)
            if not dest.startswith('/'):
                dest = self._get_absolute_path(path=dest)

        self._task.args['src'] = src
        self._task.args['dest'] = dest

        # Allow custom rsync path argument
        rsync_path = self._task.args.get('rsync_path', None)

        # If no rsync_path is set, sudo was originally set, and dest is remote then add 'sudo rsync' argument
        if not rsync_path and transport_overridden and self._play_context.become and self._play_context.become_method == 'sudo' and not dest_is_local:
            rsync_path = 'sudo rsync'

        # make sure rsync path is quoted.
        if rsync_path:
            self._task.args['rsync_path'] = '"%s"' % rsync_path

        if use_ssh_args:
            self._task.args['ssh_args'] = C.ANSIBLE_SSH_ARGS

        # run the module and store the result
        result.update(self._execute_module('synchronize', task_vars=task_vars))

        if 'SyntaxError' in result['msg']:
            # Emit a warning about using python3 because synchronize is
            # somewhat unique in running on localhost
            result['traceback'] = result['msg']
            result['msg'] = 'SyntaxError parsing module.  Perhaps invoking "python" on your local (or delegate_to) machine invokes python3.  You can set ansible_python_interpreter for localhost (or the delegate_to machine) to the location of python2 to fix this'
        return result