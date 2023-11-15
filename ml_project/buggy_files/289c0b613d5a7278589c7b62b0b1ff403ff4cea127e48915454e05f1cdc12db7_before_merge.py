    def get_plugin_title(self):
        """Get the plugin title of the parent widget."""
        # Needed for the editor stack to use its own switcher instance.
        # See spyder-ide/spyder#9469.
        return self.parent().plugin.get_plugin_title()