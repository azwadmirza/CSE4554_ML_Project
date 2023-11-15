    def ready(self):
        global client
        client = SimpleClient(app="kolibri", storage_path=settings.QUEUE_JOB_STORAGE_PATH)
        client.clear(force=True)