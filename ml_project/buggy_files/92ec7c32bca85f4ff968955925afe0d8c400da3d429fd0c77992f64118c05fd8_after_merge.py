    def from_contents(contents: str, filename: str) -> "File":
        encoding = File.detect_encoding(filename, BytesIO(contents.encode("utf-8")).readline)
        return File(StringIO(contents), path=Path(filename).resolve(), encoding=encoding)