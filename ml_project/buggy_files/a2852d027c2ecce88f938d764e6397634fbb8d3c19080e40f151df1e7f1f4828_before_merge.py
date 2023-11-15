    def closeEvent(self, event):
        """Overrides QWidget closeEvent()."""
        self.threadmanager.close_all_threads()
        self.analysis_timer.timeout.disconnect(self.analyze_script)

        # Remove editor references from the outline explorer settings
        if self.outlineexplorer is not None:
            for finfo in self.data:
                self.outlineexplorer.remove_editor(finfo.editor.oe_proxy)

        QWidget.closeEvent(self, event)