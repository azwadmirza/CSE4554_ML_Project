    def _retrieve(source_key, target_key, target):
        if source_key in data:
            target[str(target_key)] = data[source_key]