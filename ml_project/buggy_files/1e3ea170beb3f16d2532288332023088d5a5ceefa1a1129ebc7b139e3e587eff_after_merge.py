    def __init__(self, bucket: str, aws_credentials_secret: str = None) -> None:
        self.bucket = bucket
        self.aws_credentials_secret = aws_credentials_secret
        self._client = None
        super().__init__()