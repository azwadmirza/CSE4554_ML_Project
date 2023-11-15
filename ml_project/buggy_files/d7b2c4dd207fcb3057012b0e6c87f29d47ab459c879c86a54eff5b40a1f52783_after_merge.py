    def get_namespace_view(self):
        """
        Return the namespace view

        This is a dictionary with the following structure

        {'a': {'color': '#800000', 'size': 1, 'type': 'str', 'view': '1'}}

        Here:
        * 'a' is the variable name
        * 'color' is the color used to show it
        * 'size' and 'type' are self-evident
        * and'view' is its value or the text shown in the last column
        """
        settings = self.namespace_view_settings
        if settings:
            ns = self._get_current_namespace()
            view = repr(make_remote_view(ns, settings, EXCLUDED_NAMES))
            return view
        else:
            return repr(None)