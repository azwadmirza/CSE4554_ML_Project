    def run(self):
        self.remote_config.set_default(
            self.args.name, unset=self.args.unset, level=self.args.level
        )
        return 0