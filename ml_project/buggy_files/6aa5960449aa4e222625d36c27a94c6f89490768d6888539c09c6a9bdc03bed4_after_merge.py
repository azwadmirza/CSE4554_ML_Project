    def copy_value(self, orig_name, new_name):
        """Copy a variable"""
        code = u"get_ipython().kernel.copy_value('%s', '%s')" % (orig_name,
                                                                 new_name)
        if self._reading:
            self.kernel_client.input(u'!' + code)
        else:
            self.silent_execute(code)