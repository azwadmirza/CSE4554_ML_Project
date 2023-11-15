    def _repeated_key_press(self, key, count=1, modifier=Qt.NoModifier):
        """Send count fake key presses to this scroller's WebEngineTab."""
        for _ in range(min(count, 1000)):
            self._tab.key_press(key, modifier)