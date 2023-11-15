    def set_color_scheme(self, color_scheme, reset=True):
        """Set IPython color scheme."""
        # Needed to handle not initialized kernel_client
        # See issue 6996
        try:
            self.shellwidget.set_color_scheme(color_scheme, reset)
        except AttributeError:
            pass