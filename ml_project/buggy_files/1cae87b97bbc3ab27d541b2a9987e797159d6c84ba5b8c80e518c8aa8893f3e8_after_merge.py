    def load(self):
        config = configparser.ConfigParser()
        config.read(self.location, encoding="utf-8")
        return config