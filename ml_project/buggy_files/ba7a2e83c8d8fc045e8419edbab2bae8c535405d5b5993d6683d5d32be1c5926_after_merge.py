    def description(self):
        return "%s; Priority %d" % (self.STATES.get(self._state, "(Invalid)"), self.priority)