    def is_completion_widget_visible(self):
        """Return True is completion list widget is visible"""
        try:
            return self.completion_widget.isVisible()
        except RuntimeError:
            # This is to avoid a RuntimeError exception when the widget is
            # already been deleted. See spyder-ide/spyder#13248.
            return False