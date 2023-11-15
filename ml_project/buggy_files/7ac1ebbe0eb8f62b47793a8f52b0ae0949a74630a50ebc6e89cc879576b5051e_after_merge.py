    def restart_kernel(self):
        """
        Restart the associanted kernel

        Took this code from the qtconsole project
        Licensed under the BSD license
        """
        sw = self.shellwidget

        # This is needed to restart the kernel without a prompt
        # when an error in stdout corrupts the debugging process.
        # See issue 4003
        if not sw._input_reply_failed:
            message = _('Are you sure you want to restart the kernel?')
            buttons = QMessageBox.Yes | QMessageBox.No
            result = QMessageBox.question(self, _('Restart kernel?'),
                                          message, buttons)
        else:
            result = None

        if result == QMessageBox.Yes or sw._input_reply_failed:
            if sw.kernel_manager:
                if self.infowidget.isVisible():
                    self.infowidget.hide()
                    sw.show()
                try:
                    sw.kernel_manager.restart_kernel()
                except RuntimeError as e:
                    sw._append_plain_text(
                        _('Error restarting kernel: %s\n') % e,
                        before_prompt=True
                    )
                else:
                    sw.reset(clear=not sw._input_reply_failed)
                    if sw._input_reply_failed:
                        sw._append_html(_("<br>Restarting kernel because "
                                        "an error occurred while "
                                        "debugging\n<hr><br>"),
                                        before_prompt=False)
                        sw._input_reply_failed = False
                    else:
                        sw._append_html(_("<br>Restarting kernel...\n<hr><br>"),
                                before_prompt=False)
            else:
                sw._append_plain_text(
                    _('Cannot restart a kernel not started by Spyder\n'),
                    before_prompt=True
                )