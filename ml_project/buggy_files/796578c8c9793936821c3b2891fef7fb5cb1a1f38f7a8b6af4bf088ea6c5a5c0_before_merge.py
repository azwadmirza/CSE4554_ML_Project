    def set_value(self, name, value):
        """Set value for a variable"""
        value = to_text_string(value)
        self.silent_execute("get_ipython().kernel.set_value('%s', %s)" %
                            (name, value))