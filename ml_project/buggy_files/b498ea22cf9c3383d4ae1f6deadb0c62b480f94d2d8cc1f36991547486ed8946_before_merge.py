    def create(self):
        """
        Calls Docker API to creates the Docker container instance. Creating the container does *not* run the container.
        Use ``start`` method to run the container

        :return string: ID of the created container
        :raise RuntimeError: If this method is called after a container already has been created
        """

        if self.is_created():
            raise RuntimeError("This container already exists. Cannot create again.")

        LOG.info("Mounting %s as %s:ro inside runtime container", self._host_dir, self._working_dir)

        kwargs = {
            "command": self._cmd,
            "working_dir": self._working_dir,
            "volumes": {
                self._host_dir: {
                    # Mount the host directory as "read only" directory inside container at working_dir
                    # https://docs.docker.com/storage/bind-mounts
                    # Mount the host directory as "read only" inside container
                    "bind": self._working_dir,
                    "mode": "ro"
                }
            },
            # We are not running an interactive shell here.
            "tty": False
        }

        if self._container_opts:
            kwargs.update(self._container_opts)

        if self._additional_volumes:
            kwargs["volumes"].update(self._additional_volumes)

        # Make sure all mounts are of posix path style.
        kwargs["volumes"] = {to_posix_path(host_dir): mount for host_dir, mount in kwargs["volumes"].items()}

        if self._env_vars:
            kwargs["environment"] = self._env_vars

        if self._exposed_ports:
            kwargs["ports"] = self._exposed_ports

        if self._entrypoint:
            kwargs["entrypoint"] = self._entrypoint

        if self._memory_limit_mb:
            # Ex: 128m => 128MB
            kwargs["mem_limit"] = "{}m".format(self._memory_limit_mb)

        real_container = self.docker_client.containers.create(self._image, **kwargs)
        self.id = real_container.id

        if self.network_id:
            network = self.docker_client.networks.get(self.network_id)
            network.connect(self.id)

        return self.id