    def stop(self):
        """Stop a managed service"""
        if not self.managed:
            raise RuntimeError("Cannot stop unmanaged service %s" % self)
        if self.spawner:
            self.spawner.stop_polling()
            return self.spawner.stop()