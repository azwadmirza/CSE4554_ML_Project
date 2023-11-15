    def run(self):
        self.remote_config.modify(
            self.args.name,
            self.args.option,
            self.args.value,
            level=self.args.level,
        )
        return 0