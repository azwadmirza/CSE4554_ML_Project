    def run(self):
        self.config.set_dir(self.args.value, level=self.args.level)
        return 0