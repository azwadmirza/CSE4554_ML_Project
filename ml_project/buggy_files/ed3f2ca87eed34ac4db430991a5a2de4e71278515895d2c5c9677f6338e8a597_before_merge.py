    def _deserialize(path):
        serial = salt.payload.Serial(__opts__)
        ret = {'accumulators': {}, 'accumulators_deps': {}}
        try:
            with open(path, 'rb') as f:
                loaded = serial.load(f)
                return loaded if loaded else ret
        except IOError:
            return ret