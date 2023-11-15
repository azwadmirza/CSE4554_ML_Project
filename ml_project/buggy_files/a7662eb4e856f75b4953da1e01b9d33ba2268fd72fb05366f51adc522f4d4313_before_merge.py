    def save(self, args, kwargs):
        from knack.util import ensure_dir
        directory, filename = self._get_cached_object_path(args, kwargs)
        ensure_dir(directory)
        with open(os.path.join(directory, filename), 'w') as f:
            logger.info(
                "Caching %s '%s' as: %s", self._model_type, self._resource_name,
                os.path.join(directory, filename)
            )
            self._dump_to_file(f)