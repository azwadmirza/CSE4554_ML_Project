    def __init__(self, environ, parent=None):
        super(RemoteEnvDialog, self).__init__(parent)
        try:
            self.setup(
                envdict2listdict(environ),
                title=_("Environment variables"),
                width=700,
                readonly=True,
                icon=ima.icon('environ')
            )
        except Exception as e:
            QMessageBox.warning(
                parent,
                _("Warning"),
                _("An error occurred while trying to show your "
                  "environment variables. The error was<br><br>"
                  "<tt>{0}</tt>").format(e),
                QMessageBox.Ok
            )