    def get_value(self, name):
        """Get the value of a variable"""
        ns = self._get_current_namespace()
        value = ns[name]
        try:
            publish_data({'__spy_data__': value})
        except:
            # * There is no need to inform users about
            #   these errors.
            # * value = None makes Spyder to ignore
            #   petitions to display a value
            value = None
            publish_data({'__spy_data__': value})