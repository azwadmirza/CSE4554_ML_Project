    def run(self):
        self.remote_config.add(
            self.args.name,
            self.args.url,
            force=self.args.force,
            default=self.args.default,
            level=self.args.level,
        )
        return 0