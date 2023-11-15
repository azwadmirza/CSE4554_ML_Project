    def set_value(self, name, value):
        """Set value for a variable"""
        value = to_text_string(value)
        code = u"get_ipython().kernel.set_value('%s', %s)" % (name, value)
        if self._reading:
            self.kernel_client.input(u'!' + code)
        else:
            self.silent_execute(code)