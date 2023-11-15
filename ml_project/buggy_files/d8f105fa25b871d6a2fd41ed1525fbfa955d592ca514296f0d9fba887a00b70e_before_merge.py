    def __display_right(self, stat_display):
        """Display the right sidebar in the Curses interface.

        docker + processcount + amps + processlist + alert
        """
        # Do not display anything if space is not available...
        if self.screen.getmaxyx()[1] < self._left_sidebar_min_width:
            return

        # Restore line position
        self.next_line = self.saved_line

        # Display right sidebar
        self.new_column()
        for p in self._right_sidebar:
            self.new_line()
            if p == 'processlist':
                self.display_plugin(stat_display['processlist'],
                                    display_optional=(self.screen.getmaxyx()[1] > 102),
                                    display_additional=(not MACOS),
                                    max_y=(self.screen.getmaxyx()[0] - self.get_stats_display_height(stat_display['alert']) - 2))
            else:
                self.display_plugin(stat_display[p])