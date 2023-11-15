    def run(self):
        for name, url in self.config.list(level=self.args.level).items():
            logger.info("{}\t{}".format(name, url))
        return 0