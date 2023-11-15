    def ready(self):
        from kolibri.tasks.api import client
        client.clear(force=True)