    def settings_to_widget(self, widget, *_args):
        context = widget.current_context
        if context is None:
            return
        pairs = context.values.get("attr_pairs", [])
        widget.attr_pairs = [self.decode_pair(widget, pair) for pair in pairs]