    def delete(self):
        # Make sure the _ds_listener is deleted before the _ds_driver
        self._ds_listener = None