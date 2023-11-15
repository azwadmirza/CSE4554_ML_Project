    def save(self, args, kwargs):
        from knack.util import ensure_dir
        directory, filename = self.path(args, kwargs)
        ensure_dir(directory)
        with open(os.path.join(directory, filename), 'w') as f:
            logger.info(
                "Caching %s '%s' as: %s", self._model_name, self._resource_name,
                os.path.join(directory, filename)
            )
            self.last_saved = str(datetime.datetime.now())
            self._dump_to_file(f)