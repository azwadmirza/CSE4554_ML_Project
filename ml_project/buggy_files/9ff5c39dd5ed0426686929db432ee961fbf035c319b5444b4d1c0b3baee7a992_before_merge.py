    def shutdown(self) -> None:
        """Completely shut down the connected Serve instance.

        Shuts down all processes and deletes all state associated with the
        instance.
        """
        if not self._shutdown:
            ray.get(self._controller.shutdown.remote())
            ray.kill(self._controller, no_restart=True)
            self._shutdown = True