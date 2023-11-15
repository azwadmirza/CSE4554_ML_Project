    def check_app_installed(self):
        """Overrides superclass."""
        if not self._adb_grep_wrapper(
            "pm list package | grep com.googlecode.android_scripting"):
            raise jsonrpc_client_base.AppStartError(
                '%s is not installed on %s' % (
                self.app_name, self._adb.serial))