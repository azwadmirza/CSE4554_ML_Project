    def _complete_command(self):
        retval = []
        if self.current_word == self.command_name:
            if self.command_hc:
                retval = self.command_hc.command_table.keys()
        elif self.current_word.startswith('-'):
            retval = self._find_possible_options()
        else:
            # See if they have entered a partial command name
            if self.command_hc:
                retval = [n for n in self.command_hc.command_table
                          if n.startswith(self.current_word)]
        return retval