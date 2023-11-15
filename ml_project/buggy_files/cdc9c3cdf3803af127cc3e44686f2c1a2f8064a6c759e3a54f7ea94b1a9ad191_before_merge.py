    def run_rsync_up(self, source, target):
        protected_path = target
        if target.find("/root") == 0:
            target = target.replace("/root", "/tmp/root")
        self.ssh_command_runner.run(
            f"mkdir -p {os.path.dirname(target.rstrip('/'))}")
        self.ssh_command_runner.run_rsync_up(source, target)
        if self._check_container_status():
            self.ssh_command_runner.run("docker cp {} {}:{}".format(
                target, self.docker_name,
                self._docker_expand_user(protected_path)))