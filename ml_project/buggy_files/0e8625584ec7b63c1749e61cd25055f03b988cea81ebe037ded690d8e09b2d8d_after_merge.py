    def loads(cls, text):
        result = []
        for line in text.splitlines():
            if not line.strip():
                continue
            name, value = line.split("=", 1)
            result.append((name.strip(), value.strip()))
        return cls.from_list(result)