    def __init__(
        self,
        filename: Union[str, Path],
    ):
        super().__init__(f"Unknown or unsupported encoding in {filename}")
        self.filename = filename