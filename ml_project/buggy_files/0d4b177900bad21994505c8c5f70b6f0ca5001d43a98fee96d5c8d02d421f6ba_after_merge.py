    def _save(self, data: tf.keras.Model) -> None:
        save_path = get_filepath_str(self._get_save_path(), self._protocol)

        # Make sure all intermediate directories are created.
        save_dir = Path(save_path).parent
        save_dir.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix=self._tmp_prefix) as path:
            if self._is_h5:
                path = str(PurePath(path) / TEMPORARY_H5_FILE)

            tf.keras.models.save_model(data, path, **self._save_args)

            # Use fsspec to take from local tempfile directory/file and
            # put in ArbitraryFileSystem
            if self._is_h5:
                self._fs.copy(path, save_path)
            else:
                self._fs.put(path, save_path, recursive=True)