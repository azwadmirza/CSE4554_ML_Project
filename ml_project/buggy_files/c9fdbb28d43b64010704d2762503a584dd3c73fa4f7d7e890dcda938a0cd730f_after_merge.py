    def stop(self):
        try:
            self.log.debug("Stopping core...")
            # self.evm.fire('pyload:stopping')

            for thread in self.thread_manager.threads:
                thread.put("quit")

            for pyfile in list(self.files.cache.values()):
                pyfile.abort_download()

            self.addon_manager.core_exiting()

        finally:
            self.files.sync_save()
            self._running.clear()