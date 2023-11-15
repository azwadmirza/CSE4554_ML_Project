    def settings_to_widget(self, widget, *_args):
        context = widget.current_context
        if context is None:
            return
        pairs = context.values.get("attr_pairs")
        if pairs:
            # attr_pairs is schema only setting which means it is not always
            # present. When not present leave widgets default.
            widget.attr_pairs = [
                self.decode_pair(widget, pair) for pair in pairs
            ]