    def ready(self):
        load_core_settings()

        # Import these to force registration of checks and signals
        from . import checks  # noqa:F401
        from . import handlers

        signals.post_migrate.connect(handlers.create_local_config, sender=self)