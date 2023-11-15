    def stop(self):
        """Stop a managed service"""
        if not self.managed:
            raise RuntimeError("Cannot stop unmanaged service %s" % self)
        if self.spawner:
            if self.orm.server:
                self.db.delete(self.orm.server)
                self.db.commit()
            self.spawner.stop_polling()
            return self.spawner.stop()