    def check_app_installed(self):
        """Overrides superclass."""
        # Check that the Mobly Snippet app is installed.
        out = self._adb.shell('pm list package')
        if not self._grep('^package:%s$' % self.package, out):
            raise jsonrpc_client_base.AppStartError(
                '%s is not installed on %s' % (self.package, self._serial))
        # Check that the app is instrumented.
        out = self._adb.shell('pm list instrumentation')
        matched_out = self._grep('^instrumentation:%s/%s' % (
            self.package, _INSTRUMENTATION_RUNNER_PACKAGE), out)
        if not matched_out:
            raise jsonrpc_client_base.AppStartError(
                '%s is installed on %s, but it is not instrumented.' %
                (self.package, self._serial))
        match = re.search('^instrumentation:(.*)\/(.*) \(target=(.*)\)$',
                          matched_out[0])
        target_name = match.group(3)
        # Check that the instrumentation target is installed if it's not the
        # same as the snippet package.
        if target_name != self.package:
            out = self._adb.shell('pm list package')
            if not self._grep('^package:%s$' % target_name, out):
                raise jsonrpc_client_base.AppStartError(
                    'Instrumentation target %s is not installed on %s' %
                    (target_name, self._serial))