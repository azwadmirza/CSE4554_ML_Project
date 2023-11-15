    def append_event(self, ev):
        """Create a new KeySequence object with the given QKeyEvent added."""
        key = ev.key()
        modifiers = ev.modifiers()

        _assert_plain_key(key)
        _assert_plain_modifier(modifiers)

        if key == 0x0:
            raise KeyParseError(None, "Got nil key!")

        # We always remove Qt.GroupSwitchModifier because QKeySequence has no
        # way to mention that in a binding anyways...
        modifiers &= ~Qt.GroupSwitchModifier

        # We change Qt.Key_Backtab to Key_Tab here because nobody would
        # configure "Shift-Backtab" in their config.
        if modifiers & Qt.ShiftModifier and key == Qt.Key_Backtab:
            key = Qt.Key_Tab

        # We don't care about a shift modifier with symbols (Shift-: should
        # match a : binding even though we typed it with a shift on an
        # US-keyboard)
        #
        # However, we *do* care about Shift being involved if we got an
        # upper-case letter, as Shift-A should match a Shift-A binding, but not
        # an "a" binding.
        #
        # In addition, Shift also *is* relevant when other modifiers are
        # involved. Shift-Ctrl-X should not be equivalent to Ctrl-X.
        if (modifiers == Qt.ShiftModifier and
                _is_printable(ev.key()) and
                not ev.text().isupper()):
            modifiers = Qt.KeyboardModifiers()

        keys = list(self._iter_keys())
        keys.append(key | int(modifiers))

        return self.__class__(*keys)