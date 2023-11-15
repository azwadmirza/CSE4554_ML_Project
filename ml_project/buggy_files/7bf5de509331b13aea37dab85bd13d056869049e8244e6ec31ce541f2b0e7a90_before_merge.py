    def __getitem__(self, key):
        """
        Flask templates always expects a None when key is not found in config
        """
        return self.get(key)