    def set_value(self, name, value):
        """Set value for a variable"""
        self.call_kernel(interrupt=True, blocking=False
                         ).set_value(name, value)