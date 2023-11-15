    def _retrieve_tar(self, model_path: Text) -> None:
        """Downloads a model that has previously been persisted to s3."""
        tar_name = os.path.basename(model_path)
        with open(tar_name, "wb") as f:
            self.bucket.download_fileobj(model_path, f)