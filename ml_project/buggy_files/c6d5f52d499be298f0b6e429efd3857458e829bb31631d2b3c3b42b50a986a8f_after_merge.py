    def __del__(self):
        try:
            self._unload()
        except ModuleNotFoundError:
            pass  # has probably been garbage-collected already