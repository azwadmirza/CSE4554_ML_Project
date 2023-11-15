    def _minimum_tab_size_hint_helper(self, tab_text: str,
                                      icon_width: int,
                                      ellipsis: bool, pinned: bool) -> QSize:
        """Helper function to cache tab results.

        Config values accessed in here should be added to _on_config_changed to
        ensure cache is flushed when needed.
        """
        text = '\u2026' if ellipsis else tab_text
        # Don't ever shorten if text is shorter than the ellipsis

        def _text_to_width(text):
            # Calculate text width taking into account qt mnemonics
            return self.fontMetrics().size(Qt.TextShowMnemonic, text).width()
        text_width = min(_text_to_width(text),
                         _text_to_width(tab_text))
        padding = config.val.tabs.padding
        indicator_width = config.val.tabs.indicator.width
        indicator_padding = config.val.tabs.indicator.padding
        padding_h = padding.left + padding.right
        # Only add padding if indicator exists
        if indicator_width != 0:
            padding_h += indicator_padding.left + indicator_padding.right
        padding_v = padding.top + padding.bottom
        height = self.fontMetrics().height() + padding_v
        width = (text_width + icon_width +
                 padding_h + indicator_width)
        min_width = config.val.tabs.min_width
        if (not self.vertical and min_width > 0 and
                not pinned or not config.val.tabs.pinned.shrink):
            width = max(min_width, width)
        return QSize(width, height)