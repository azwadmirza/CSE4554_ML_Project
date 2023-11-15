    def from_contents(contents: str, filename: str) -> "File":
        encoding, _ = tokenize.detect_encoding(BytesIO(contents.encode("utf-8")).readline)
        return File(StringIO(contents), path=Path(filename).resolve(), encoding=encoding)