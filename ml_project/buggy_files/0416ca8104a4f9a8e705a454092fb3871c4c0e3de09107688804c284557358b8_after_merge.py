    def save(self, item):
        item.modes.append(model.TriggerMode.HOTKEY)

        # Build modifier list
        modifiers = self.build_modifiers()

        if self.key in self.REVERSE_KEY_MAP:
            key = self.REVERSE_KEY_MAP[self.key]
        else:
            key = self.key

        if key is None:
            raise RuntimeError("Attempt to set hotkey with no key")
        logger.info("Item {} updated with hotkey {} and modifiers {}".format(item, key, modifiers))
        item.set_hotkey(modifiers, key)