    def get_doc(self, objtxt):
        """Get object documentation dictionary"""
        try:
            return self.call_kernel(interrupt=True, blocking=True
                                    ).get_doc(objtxt)
        except (TimeoutError, UnpicklingError):
            return None