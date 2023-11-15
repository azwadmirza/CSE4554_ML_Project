    def make_filename(cls, entry):
        return entry.date.strftime(
            "%Y-%m-%d_{}.{}".format(cls._slugify(str(entry.title)), cls.extension)
        )