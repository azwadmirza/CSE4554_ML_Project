    def clear_console(self):
        if self._reading:
            self.dbg_exec_magic('clear')
        else:
            self.execute("%clear")