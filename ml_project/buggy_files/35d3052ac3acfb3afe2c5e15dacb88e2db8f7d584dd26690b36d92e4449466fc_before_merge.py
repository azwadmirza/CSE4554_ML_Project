def read_file(filename: Text, encoding: Text = "utf-8") -> Any:
    """Read text from a file."""
    with open(filename, encoding=encoding) as f:
        return f.read()