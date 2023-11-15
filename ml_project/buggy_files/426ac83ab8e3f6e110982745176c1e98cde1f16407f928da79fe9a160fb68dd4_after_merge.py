    def remove_value(self, name):
        """Remove a variable"""
        code = u"get_ipython().kernel.remove_value('%s')" % name
        if self._reading:
            self.kernel_client.input(u'!' + code)
        else:
            self.silent_execute(code)