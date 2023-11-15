    def retrieve(self, model_name: Text, target_path: Text) -> None:
        """Downloads a model that has been persisted to cloud storage."""

        tar_name = model_name

        if not model_name.endswith("tar.gz"):
            # ensure backward compatibility
            tar_name = self._tar_name(model_name)

        self._retrieve_tar(tar_name)
        self._decompress(tar_name, target_path)