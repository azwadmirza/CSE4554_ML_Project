    def run_rsync_up(self, source, target):
        self.set_ssh_ip_if_required()
        self.process_runner.check_call([
            "rsync", "--rsh",
            " ".join(["ssh"] + self.get_default_ssh_options(120)), "-avz",
            source, "{}@{}:{}".format(self.ssh_user, self.ssh_ip, target)
        ])