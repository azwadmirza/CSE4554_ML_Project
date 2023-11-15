    def remove_value(self, name):
        """Remove a variable"""
        self.silent_execute("get_ipython().kernel.remove_value('%s')" % name)