    def refresh(self, nolock=False):
        """
        Force refresh the display of this bar
        """
        if self.disable:
            return

        if not nolock:
            self._lock.acquire()
        self.moveto(abs(self.pos))
        self.sp(self.__repr__())
        self.moveto(-abs(self.pos))
        if not nolock:
            self._lock.release()