    def verify_tools(self):
        super().verify_tools()

        try:
            print()
            print("Ensure we have the linuxdeploy AppImage...")
            self.linuxdeploy_appimage = self.download_url(
                url=self.linuxdeploy_download_url,
                download_path=self.dot_briefcase_path / 'tools'
            )
            self.os.chmod(str(self.linuxdeploy_appimage), 0o755)
        except requests_exceptions.ConnectionError:
            raise NetworkFailure('downloading linuxdeploy AppImage')