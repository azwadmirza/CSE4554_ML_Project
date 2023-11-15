    def parse(self, file):
        file = EncodedIO(file)
        file = io.TextIOWrapper(file, encoding=file.encoding)
        while True:
            batch = list(itertools.islice(file, settings.IMPORT_BATCH_SIZE))
            if not batch:
                break
            yield [{'text': line.strip()} for line in batch]