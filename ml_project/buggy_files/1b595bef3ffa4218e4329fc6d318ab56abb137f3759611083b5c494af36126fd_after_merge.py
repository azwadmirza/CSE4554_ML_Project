    def found_wake_word(self, frame_data):
        """Check if wakeword has been found.

        Returns:
            (bool) True if wakeword was found otherwise False.
        """
        if self.has_found:
            self.has_found = False
            return True
        return False