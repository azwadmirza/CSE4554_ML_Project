    def load(self, args, kwargs):
        directory, filename = self.path(args, kwargs)
        with open(os.path.join(directory, filename), 'r') as f:
            logger.info(
                "Loading %s '%s' from cache: %s", self._model_name, self._resource_name,
                os.path.join(directory, filename)
            )
            obj_data = json.loads(f.read())
            self._payload = obj_data['_payload']
            self.last_saved = obj_data['last_saved']
        self._payload = self.result()