    def run(self, tmp=None, task_vars=None):

        self.load_provider()

        provider = self._task.args['provider']

        pc = copy.deepcopy(self._play_context)
        pc.connection = 'network_cli'
        pc.port = provider['port'] or self._play_context.port
        pc.remote_user = provider['username'] or self._play_context.connection_user
        pc.password = provider['password'] or self._play_context.password
        pc.become = provider['authorize'] or False
        pc.become_pass = provider['auth_pass']

        socket_path = self._get_socket_path(pc)
        if not os.path.exists(socket_path):
            # start the connection if it isn't started
            connection = self._shared_loader_obj.connection_loader.get('persistent', pc, sys.stdin)
            connection.exec_command('EXEC: show version')

        task_vars['ansible_socket'] = socket_path

        if self._play_context.become_method == 'enable':
            self._play_context.become = False
            self._play_context.become_method = None

        return super(ActionModule, self).run(tmp, task_vars)