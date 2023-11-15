    def run(self):
        self.cache_config.set_dir(self.args.value, level=self.args.level)
        return 0