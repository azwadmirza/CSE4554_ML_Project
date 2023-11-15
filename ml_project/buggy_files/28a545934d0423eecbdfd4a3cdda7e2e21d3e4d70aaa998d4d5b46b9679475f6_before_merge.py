    def get_current_word(self, completion=False):
        """Return current word, i.e. word at cursor position"""
        ret = self.get_current_word_and_position(completion)
        if ret is not None:
            return ret[0]