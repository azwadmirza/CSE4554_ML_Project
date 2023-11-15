    def _maybe_fire_closing(self):
        if self.closing and not self.inprogress:
            if self.nextcall:
                self.nextcall.cancel()
                self.heartbeat.stop()
            self.closing.callback(None)