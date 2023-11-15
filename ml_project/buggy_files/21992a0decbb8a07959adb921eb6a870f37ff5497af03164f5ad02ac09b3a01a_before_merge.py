    def read_dict(self, dictionary, source='<dict>'):
        super().read_dict(dictionary=dictionary, source=source)
        self._validate()