    def found_wake_word(self, frame_data):
        if self.has_found:
            self.has_found = False
            return True
        return False