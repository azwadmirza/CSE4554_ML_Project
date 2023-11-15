    def run_rsync_down(self, source, target):
        self.set_ssh_ip_if_required()
        self.process_runner.check_call([
            "rsync", "--rsh",
            " ".join(["ssh"] + self.get_default_ssh_options(120)), "-avz",
            "{}@{}:{}".format(self.ssh_user, self.ssh_ip, source), target
        ])