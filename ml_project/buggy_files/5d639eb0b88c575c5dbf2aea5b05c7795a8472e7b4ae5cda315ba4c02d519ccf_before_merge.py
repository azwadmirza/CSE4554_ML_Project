    def start(self):
        """Start a managed service"""
        if not self.managed:
            raise RuntimeError("Cannot start unmanaged service %s" % self)
        self.log.info("Starting service %r: %r", self.name, self.command)
        env = {}
        env.update(self.environment)

        env['JUPYTERHUB_SERVICE_NAME'] = self.name
        env['JUPYTERHUB_API_TOKEN'] = self.api_token
        env['JUPYTERHUB_API_URL'] = self.hub_api_url
        env['JUPYTERHUB_BASE_URL'] = self.base_url
        env['JUPYTERHUB_SERVICE_PREFIX'] = self.server.base_url
        env['JUPYTERHUB_SERVICE_URL'] = self.url

        self.spawner = _ServiceSpawner(
            cmd=self.command,
            environment=env,
            api_token=self.api_token,
            cwd=self.cwd,
            user=_MockUser(
                name=self.user,
                service=self,
                server=self.orm.server,
            ),
        )
        self.spawner.start()
        self.proc = self.spawner.proc
        self.spawner.add_poll_callback(self._proc_stopped)
        self.spawner.start_polling()