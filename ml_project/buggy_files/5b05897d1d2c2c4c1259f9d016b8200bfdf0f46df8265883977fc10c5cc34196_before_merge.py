    def __init__(self, environ, parent=None):
        super(RemoteEnvDialog, self).__init__(parent)
        self.setup(envdict2listdict(environ),
                   title=_("Environment variables"),
                   width=700,
                   readonly=True,
                   icon=ima.icon('environ'))