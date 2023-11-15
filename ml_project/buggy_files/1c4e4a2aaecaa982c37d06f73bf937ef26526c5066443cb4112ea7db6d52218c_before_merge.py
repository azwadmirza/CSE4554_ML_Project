    def _retrieve_tar(self, target_filename: Text) -> None:
        """Downloads a model that has previously been persisted to s3."""

        with open(target_filename, "wb") as f:
            self.bucket.download_fileobj(target_filename, f)