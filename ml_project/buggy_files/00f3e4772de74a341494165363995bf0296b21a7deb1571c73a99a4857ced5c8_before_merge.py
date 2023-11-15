    def pull(self, container):
        command = container.build_pull_command()
        shell(command)