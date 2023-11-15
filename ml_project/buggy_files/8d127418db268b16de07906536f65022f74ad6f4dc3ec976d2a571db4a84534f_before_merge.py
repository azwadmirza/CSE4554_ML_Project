    def _process_command_line(self):
        # Process the command line and try to find:
        #     - command_name
        #     - subcommand_name
        #     - words
        #     - current_word
        #     - previous_word
        #     - non_options
        #     - options
        self.command_name = None
        self.subcommand_name = None
        self.words = self.cmdline[0:self.point].split()
        self.current_word = self.words[-1]
        if len(self.words) >= 2:
            self.previous_word = self.words[-2]
        else:
            self.previous_word = None
        self.non_options = [w for w in self.words if not w.startswith('-')]
        self.options = [w for w in self.words if w.startswith('-')]
        # Look for a command name in the non_options
        for w in self.non_options:
            if w in self.main_hc.command_table:
                self.command_name = w
                cmd_obj = self.main_hc.command_table[self.command_name]
                self.command_hc = cmd_obj.create_help_command()
                if self.command_hc.command_table:
                    # Look for subcommand name
                    for w in self.non_options:
                        if w in self.command_hc.command_table:
                            self.subcommand_name = w
                            cmd_obj = self.command_hc.command_table[self.subcommand_name]
                            self.subcommand_hc = cmd_obj.create_help_command()
                            break
                break