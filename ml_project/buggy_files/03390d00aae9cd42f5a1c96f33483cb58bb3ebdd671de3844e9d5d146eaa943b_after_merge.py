    def exists(self, location: str, **kwargs: Any) -> bool:
        """
        Checks whether the target result exists in the S3 bucket.

        Does not validate whether the result is `valid`, only that it is present.

        Args:
            - location (str): Location of the result in the specific result target.
            - **kwargs (Any): string format arguments for `location`

        Returns:
            - bool: whether or not the target result exists.
        """
        import botocore

        try:
            self.client.get_object(
                Bucket=self.bucket, Key=location.format(**kwargs)
            ).load()
        except botocore.exceptions.ClientError as exc:
            if exc.response["Error"]["Code"] == "NoSuchKey":
                return False
            raise
        except Exception as exc:
            self.logger.exception(
                "Unexpected error while reading from S3: {}".format(repr(exc))
            )
            raise
        return True