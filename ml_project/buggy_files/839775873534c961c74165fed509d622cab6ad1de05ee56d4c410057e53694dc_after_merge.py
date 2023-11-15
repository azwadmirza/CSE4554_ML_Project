    def parse(self, file):
        data = []
        file = EncodedIO(file)
        file = io.TextIOWrapper(file, encoding=file.encoding)

        # Add check exception

        field_parsers = {
            "ne": lambda line, i: conllu.parser.parse_nullable_value(line[i]),
        }

        gen_parser = conllu.parse_incr(
            file,
            fields=("form", "ne"),
            field_parsers=field_parsers
        )

        try:
            for sentence in gen_parser:
                if not sentence:
                    continue
                if len(data) >= settings.IMPORT_BATCH_SIZE:
                    yield data
                    data = []
                words, labels = [], []
                for item in sentence:
                    word = item.get("form")
                    tag = item.get("ne")

                    if tag is not None:
                        char_left = sum(map(len, words)) + len(words)
                        char_right = char_left + len(word)
                        span = [char_left, char_right, tag]
                        labels.append(span)

                    words.append(word)

                # Create and add JSONL
                data.append({'text': ' '.join(words), 'labels': labels})

        except conllu.parser.ParseException as e:
            raise FileParseException(line_num=-1, line=str(e))

        if data:
            yield data