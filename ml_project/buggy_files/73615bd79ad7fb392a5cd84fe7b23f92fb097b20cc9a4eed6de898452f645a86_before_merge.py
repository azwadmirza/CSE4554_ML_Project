    def __enter__(self):
        plugin_manager.hook.start_step(uuid=self.uuid, title=self.title, params=self.params)