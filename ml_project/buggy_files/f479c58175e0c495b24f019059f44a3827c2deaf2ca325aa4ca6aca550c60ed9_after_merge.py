    def run(self):
        self.remote_config.remove(self.args.name, level=self.args.level)
        return 0