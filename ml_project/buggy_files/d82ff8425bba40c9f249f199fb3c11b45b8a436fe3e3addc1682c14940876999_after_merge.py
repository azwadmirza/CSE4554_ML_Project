    def check_app_installed(self):
        """Overrides superclass."""
        out = self._adb('pm list package')
        if not self._grep('com.googlecode.android_scripting', out):
            raise jsonrpc_client_base.AppStartError(
                '%s is not installed on %s' % (self.app_name,
                                               self._adb.serial))