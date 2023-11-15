    def run_rsync_down(self, source, target):
        self.ssh_command_runner.run("docker cp {}:{} {}".format(
            self.docker_name, self.docker_expand_user(source), source))
        self.ssh_command_runner.run_rsync_down(source, target)