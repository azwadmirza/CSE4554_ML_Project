    def pull(self, container):
        if self.docker_cli_available:
            command = container.build_pull_command()
            shell(command)