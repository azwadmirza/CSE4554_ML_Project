    def add_unresponsive_engine(self, engine_name, error_type, error_message=None):
        self.unresponsive_engines.add((engine_name, error_type, error_message))