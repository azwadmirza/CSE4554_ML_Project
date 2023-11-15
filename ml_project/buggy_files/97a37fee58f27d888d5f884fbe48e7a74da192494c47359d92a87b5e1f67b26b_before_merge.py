    def load_byte(self, data, legacy_api=True):
        return (data if legacy_api else
                tuple(map(ord, data) if bytes is str else data))