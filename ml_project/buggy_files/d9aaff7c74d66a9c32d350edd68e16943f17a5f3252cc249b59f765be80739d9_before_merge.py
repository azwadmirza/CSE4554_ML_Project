    def ready(self):
        load_core_settings()

        from . import handlers

        signals.post_migrate.connect(handlers.create_local_config, sender=self)