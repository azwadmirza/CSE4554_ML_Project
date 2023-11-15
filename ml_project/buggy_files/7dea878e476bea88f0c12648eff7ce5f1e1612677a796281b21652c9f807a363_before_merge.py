    def getUIconfig(self):
        """Get the rendering configuration from the GUI controls."""
        # Pull internal configuration options from GUI
        self.verbose = self.verbose_mode_action.isChecked()
        #self.output = 'html'
        self.tree = self.tree_mode_action.isChecked()
        self.execcode = self.execute_code_action.isChecked()
        # If executing code, don't allow auto-mode otherwise navigation
        # can lead to getting stuck doing many recalculations
        if self.execcode:
            self.auto_mode_action.setChecked(False)
        self.auto = self.auto_mode_action.isChecked()
        self.lock_mode = self.lock_mode_action.isChecked()
        self.slideshow = self.slideshow_mode_action.isChecked()
        self.showcode = self.visible_code_action.isChecked()
        self.restoutput = self.reST_code_action.isChecked()