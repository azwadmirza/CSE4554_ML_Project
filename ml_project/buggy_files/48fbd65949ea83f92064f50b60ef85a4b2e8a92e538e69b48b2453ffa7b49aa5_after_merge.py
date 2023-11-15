    def refresh(self):
        """
        Force refresh the display of this bar
        """
        if self.disable:
            return

        self.moveto(self.pos)
        # clear up this line's content (whatever there was)
        self.clear(nomove=True)
        # Print current/last bar state
        self.fp.write(self.__repr__())
        self.moveto(-self.pos)