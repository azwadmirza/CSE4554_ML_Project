    def run(self):
        self.config.remove(self.args.name, level=self.args.level)
        return 0