    def reset_namespace(self, warning=False, silent=True, message=False):
        """Reset the namespace by removing all names defined by the user."""
        reset_str = _("Remove all variables")
        warn_str = _("All user-defined variables will be removed. "
                     "Are you sure you want to proceed?")

        if warning:
            box = MessageCheckBox(icon=QMessageBox.Warning, parent=self)
            box.setWindowTitle(reset_str)
            box.set_checkbox_text(_("Don't show again."))
            box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            box.setDefaultButton(QMessageBox.Yes)

            box.set_checked(False)
            box.set_check_visible(True)
            box.setText(warn_str)

            answer = box.exec_()

            # Update checkbox based on user interaction
            CONF.set('ipython_console', 'show_reset_namespace_warning',
                     not box.is_checked())

            if answer != QMessageBox.Yes:
                return

        try:
            if self._reading:
                self.dbg_exec_magic('reset', '-f')
            else:
                if silent:
                    if message:
                        self.reset()
                        self._append_html(_("<br><br>Removing all variables..."
                                            "\n<hr>"),
                                          before_prompt=False)
                    self.silent_execute("%reset -f")
                    self.refresh_namespacebrowser()
                else:
                    self.execute("%reset -f")

                if not self.external_kernel:
                    self.silent_execute(
                        'get_ipython().kernel.close_all_mpl_figures()')
        except AttributeError:
            pass