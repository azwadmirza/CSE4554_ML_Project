    def get_source(self, objtxt):
        """Get object source"""
        try:
            return self.call_kernel(blocking=True).get_source(objtxt)
        except (TimeoutError, UnpicklingError, RuntimeError, CommError):
            return None