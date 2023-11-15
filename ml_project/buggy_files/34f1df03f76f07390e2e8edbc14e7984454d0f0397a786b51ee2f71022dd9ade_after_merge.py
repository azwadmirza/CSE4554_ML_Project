    def clear(self, nolock=False):
        """
        Clear current bar display
        """
        if self.disable:
            return

        if not nolock:
            self._lock.acquire()
        self.moveto(abs(self.pos))
        self.sp('')
        self.fp.write('\r')  # place cursor back at the beginning of line
        self.moveto(-abs(self.pos))
        if not nolock:
            self._lock.release()