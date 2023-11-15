    def get_value(self, name):
        """Get the value of a variable"""
        ns = self._get_current_namespace()
        value = ns[name]
        publish_data({'__spy_data__': value})