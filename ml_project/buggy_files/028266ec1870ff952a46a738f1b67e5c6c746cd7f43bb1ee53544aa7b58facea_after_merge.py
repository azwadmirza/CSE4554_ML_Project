    def get_doc(self, objtxt):
        """Get object documentation dictionary"""
        try:
            return self.call_kernel(blocking=True).get_doc(objtxt)
        except (TimeoutError, UnpicklingError, RuntimeError, CommError):
            return None