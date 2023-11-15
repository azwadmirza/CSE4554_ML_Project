        def forward(self, *args, **kwargs):
            if self._heartbeat is not None:
                self._heartbeat.set()
            return super().forward(*args, **kwargs)