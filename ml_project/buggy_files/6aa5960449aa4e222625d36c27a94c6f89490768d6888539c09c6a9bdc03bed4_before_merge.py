    def copy_value(self, orig_name, new_name):
        """Copy a variable"""
        self.silent_execute("get_ipython().kernel.copy_value('%s', '%s')" %
                            (orig_name, new_name))