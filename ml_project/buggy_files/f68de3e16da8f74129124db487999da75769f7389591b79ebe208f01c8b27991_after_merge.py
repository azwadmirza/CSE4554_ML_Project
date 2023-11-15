    def start(self, workspace_folder):
        # Needed to handle an error caused by the inotify limit reached.
        # See spyder-ide/spyder#10478
        try:
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler, workspace_folder, recursive=True)
            self.observer.start()
        except OSError as e:
            if u'inotify' in to_text_string(e):
                QMessageBox.warning(
                    self.parent(),
                    "Spyder",
                    _("File system changes for this project can't be tracked "
                      "because it contains too many files. To fix this you "
                      "need to increase the inotify limit in your system, "
                      "with the following command:"
                      "<br><br>"
                      "<code>"
                      "sudo sysctl -n -w fs.inotify.max_user_watches=524288"
                      "</code>"
                      "<br><br>For a permanent solution you need to add to"
                      "<code>/etc/sysctl.conf</code>"
                      "the following line:<br><br>"
                      "<code>"
                      "fs.inotify.max_user_watches=524288"
                      "</code>"
                      "<br><br>"
                      "After doing that, you need to close and start Spyder "
                      "again so those changes can take effect."))
                self.observer = None
            else:
                raise e