    def run(self):
        """Handle the connection with the server.
        """
        # Set up the zmq port.
        self.socket = self.context.socket(zmq.PAIR)
        self.port = self.socket.bind_to_random_port('tcp://*')

        # Set up the process.
        self.process = QProcess(self)
        if self.cwd:
            self.process.setWorkingDirectory(self.cwd)
        p_args = ['-u', self.target, str(self.port)]
        if self.extra_args is not None:
            p_args += self.extra_args

        # Set up environment variables.
        processEnvironment = QProcessEnvironment()
        env = self.process.systemEnvironment()
        if (self.env and 'PYTHONPATH' not in self.env) or self.env is None:
            python_path = osp.dirname(get_module_path('spyder'))
            # Add the libs to the python path.
            for lib in self.libs:
                try:
                    path = osp.dirname(imp.find_module(lib)[1])
                    python_path = osp.pathsep.join([python_path, path])
                except ImportError:
                    pass
            env.append("PYTHONPATH=%s" % python_path)
        if self.env:
            env.update(self.env)
        for envItem in env:
            envName, separator, envValue = envItem.partition('=')
            processEnvironment.insert(envName, envValue)
        self.process.setProcessEnvironment(processEnvironment)

        # Start the process and wait for started.
        self.process.start(self.executable, p_args)
        self.process.finished.connect(self._on_finished)
        running = self.process.waitForStarted()
        if not running:
            # Don't raise an error if the plugin fails to start
            # Fixes issue 8934
            debug_print('Could not start %s' % self)
            return

        # Set up the socket notifer.
        fid = self.socket.getsockopt(zmq.FD)
        self.notifier = QSocketNotifier(fid, QSocketNotifier.Read, self)
        self.notifier.activated.connect(self._on_msg_received)