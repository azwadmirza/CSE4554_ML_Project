    def verify_tools(self):
        super().verify_tools()
        self.linuxdeploy_appimage_path = verify_linuxdeploy(self)