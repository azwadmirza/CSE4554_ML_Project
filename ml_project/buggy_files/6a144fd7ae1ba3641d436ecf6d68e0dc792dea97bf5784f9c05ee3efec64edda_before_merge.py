    def parse(self, file):
        file = io.TextIOWrapper(file, encoding='utf-8')
        data = []
        for i, line in enumerate(file, start=1):
            if len(data) >= settings.IMPORT_BATCH_SIZE:
                yield data
                data = []
            try:
                j = json.loads(line)
                j['meta'] = json.dumps(j.get('meta', {}))
                data.append(j)
            except json.decoder.JSONDecodeError:
                raise FileParseException(line_num=i, line=line)
        if data:
            yield data