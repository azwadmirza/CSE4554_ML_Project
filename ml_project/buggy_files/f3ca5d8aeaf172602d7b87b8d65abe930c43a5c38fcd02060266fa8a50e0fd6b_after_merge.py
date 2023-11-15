    def load(cls, filename):
        """Return a cache loaded from a file"""
        try:
            with open(filename, "r") as f:
                cache = json.load(f)
        except (FileNotFoundError, ValueError):
            cache = {}

        result = Cache(cache)

        def save():
            """Overwrite the original file with current cache contents"""
            with open(filename, "w") as f:
                json.dump(result.values, f)

        result.save = save
        return result