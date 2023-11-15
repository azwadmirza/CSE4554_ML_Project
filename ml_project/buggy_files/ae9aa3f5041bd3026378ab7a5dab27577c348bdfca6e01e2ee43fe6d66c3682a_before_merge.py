    def load(self, args, kwargs):
        directory, filename = self._get_cached_object_path(args, kwargs)
        with open(os.path.join(directory, filename), 'r') as f:
            logger.info(
                "Loading %s '%s' from cache: %s", self._model_type, self._resource_name,
                os.path.join(directory, filename)
            )
            obj_data = json.loads(f.read())
            self._payload = obj_data['_payload']
        # need to save the lastTouched metadata when retrieved
        with open(os.path.join(directory, filename), 'w') as f:
            self._dump_to_file(f)
        self._payload = self.result()