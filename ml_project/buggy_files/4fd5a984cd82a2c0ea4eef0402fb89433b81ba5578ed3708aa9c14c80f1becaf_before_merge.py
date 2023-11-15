    def remove_value(self, name):
        """Remove a variable"""
        self.call_kernel(interrupt=True, blocking=False
                         ).remove_value(name)