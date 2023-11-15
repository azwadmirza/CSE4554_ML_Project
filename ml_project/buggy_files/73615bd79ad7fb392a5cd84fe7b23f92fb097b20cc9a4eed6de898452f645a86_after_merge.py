    def __enter__(self):
        args, kwargs = self.params
        args.update(kwargs)
        params = list(args.items())
        plugin_manager.hook.start_step(uuid=self.uuid, title=self.title, params=params)