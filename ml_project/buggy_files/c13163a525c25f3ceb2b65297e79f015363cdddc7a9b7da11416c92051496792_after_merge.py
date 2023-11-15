    def start(self):
        try:
            if not self.enabled:
                return
            installed, path = check_if_kite_installed()
            if not installed:
                return
            logger.debug('Kite was found on the system: {0}'.format(path))
            running = check_if_kite_running()
            if running:
                return
            logger.debug('Starting Kite service...')
            self.kite_process = run_program(path)
        except OSError:
            installed, path = check_if_kite_installed()
            logger.debug(
                'Error starting Kite service at {path}...'.format(path=path))
            if self.get_option('show_installation_error_message'):
                box = MessageCheckBox(
                    icon=QMessageBox.Critical, parent=self.main)
                box.setWindowTitle(_("Kite installation error"))
                box.set_checkbox_text(_("Don't show again."))
                box.setStandardButtons(QMessageBox.Ok)
                box.setDefaultButton(QMessageBox.Ok)

                box.set_checked(False)
                box.set_check_visible(True)
                box.setText(
                    _("It seems that your Kite installation is faulty. "
                      "If you want to use Kite, please remove the "
                      "directory that appears bellow, "
                      "and try a reinstallation:<br><br>"
                      "<code>{kite_dir}</code>".format(
                          kite_dir=osp.dirname(path))))

                box.exec_()

                # Update checkbox based on user interaction
                self.set_option(
                    'show_installation_error_message', not box.is_checked())
        finally:
            # Always start client to support possibly undetected Kite builds
            self.client.start()