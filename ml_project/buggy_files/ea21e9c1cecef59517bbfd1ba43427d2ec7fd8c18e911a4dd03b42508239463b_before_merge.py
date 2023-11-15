    def get(self, section, option, literal_eval=True):
        with self.lock:
            value = RawConfigParser.get(self, section, option) if RawConfigParser.has_option(
                self, section, option) else None
            if literal_eval:
                try:
                    value = ast.literal_eval(value)
                except:
                    pass
            return value