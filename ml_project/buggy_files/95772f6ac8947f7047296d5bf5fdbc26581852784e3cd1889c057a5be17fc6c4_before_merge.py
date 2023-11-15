    def get_source(self, objtxt):
        """Get object source"""
        try:
            return self.call_kernel(interrupt=True, blocking=True
                                    ).get_source(objtxt)
        except (TimeoutError, UnpicklingError, RuntimeError):
            return None