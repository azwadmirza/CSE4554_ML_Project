    def execute_code(self, lines, clear_variables=False):
        """Execute code instructions."""
        sw = self.get_current_shellwidget()
        if sw is not None:
            if sw._reading:
                pass
            else:
                if clear_variables:
                    sw.reset_namespace(force=True)
                sw.execute(to_text_string(to_text_string(lines)))
            self.activateWindow()
            self.get_current_client().get_control().setFocus()