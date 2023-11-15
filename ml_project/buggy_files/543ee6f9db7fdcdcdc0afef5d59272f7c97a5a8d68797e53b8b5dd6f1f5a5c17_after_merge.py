    def widgets(self):
        """Get a list of open tab widgets.

        We don't implement this as generator so we can delete tabs while
        iterating over the list.
        """
        widgets = []
        for i in range(self.widget.count()):
            widget = self.widget.widget(i)
            if widget is None:
                log.webview.debug("Got None-widget in tabbedbrowser!")
            else:
                widgets.append(widget)
        return widgets