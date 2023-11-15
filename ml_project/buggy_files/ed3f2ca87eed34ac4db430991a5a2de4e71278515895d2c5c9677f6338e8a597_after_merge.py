    def _deserialize(path):
        serial = salt.payload.Serial(__opts__)
        ret = {'accumulators': {}, 'accumulators_deps': {}}
        try:
            with open(path, 'rb') as f:
                loaded = serial.load(f)
                return loaded if loaded else ret
        except (IOError, NameError):
            # NameError is a msgpack error from salt-ssh
            return ret