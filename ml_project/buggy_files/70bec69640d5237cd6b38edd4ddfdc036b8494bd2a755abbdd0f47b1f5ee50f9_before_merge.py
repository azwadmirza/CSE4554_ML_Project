    def initialize_client(self) -> None:
        """
        Initializes an S3 Client.
        """
        import boto3

        aws_access_key = None
        aws_secret_access_key = None

        if self.aws_credentials_secret:
            aws_credentials = Secret(self.aws_credentials_secret).get()
            if isinstance(aws_credentials, str):
                aws_credentials = json.loads(aws_credentials)

            aws_access_key = aws_credentials["ACCESS_KEY"]
            aws_secret_access_key = aws_credentials["SECRET_ACCESS_KEY"]

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.client = s3_client