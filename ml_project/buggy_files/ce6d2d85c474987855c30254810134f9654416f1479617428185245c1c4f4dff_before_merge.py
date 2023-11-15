    def mousePressEvent(self, event):
        # Check if mouse press happens on a layer properties widget or
        # a child of such a widget. If not, the press has happended on the
        # Layers Widget itself and should be ignored.
        widget = self.childAt(event.pos())
        layer = (
            getattr(widget, 'layer', None)
            or getattr(widget.parentWidget(), 'layer', None)
            or getattr(widget.parentWidget().parentWidget(), 'layer', None)
        )

        if layer is not None:
            self.drag_start_position = event.pos()
            self.drag_name = layer.name
        else:
            self.drag_name = None