    def debug_file(self):
        """Debug current script"""
        self.run_file(debug=True)
        # Fixes 2034
        editor = self.get_current_editor()
        if editor.get_breakpoints():
            time.sleep(0.5)
            self.debug_command('continue')