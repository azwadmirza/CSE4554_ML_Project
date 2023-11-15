    def copy_value(self, orig_name, new_name):
        """Copy a variable"""
        self.call_kernel(interrupt=True, blocking=False
                         ).copy_value(orig_name, new_name)