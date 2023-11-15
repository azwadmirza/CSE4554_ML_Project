    def set_value(self, name, value):
        """Set value for a variable"""
        self.call_kernel(
            interrupt=True,
            blocking=False,
            display_error=True,
            ).set_value(name, value)