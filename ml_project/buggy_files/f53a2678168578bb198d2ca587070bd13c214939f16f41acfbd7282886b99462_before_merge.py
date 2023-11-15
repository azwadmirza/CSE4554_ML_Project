    def check_app_installed(self):
        """Overrides superclass."""
        # Check that the Mobly Snippet app is installed.
        if not self._adb_grep_wrapper(
                r'pm list package | tr -d "\r" | grep "^package:%s$"' %
                self.package):
            raise jsonrpc_client_base.AppStartError(
                '%s is not installed on %s' % (self.package, self._serial))
        # Check that the app is instrumented.
        out = self._adb_grep_wrapper(
            r'pm list instrumentation | tr -d "\r" | grep ^instrumentation:%s/%s'
            % (self.package, _INSTRUMENTATION_RUNNER_PACKAGE))
        if not out:
            raise jsonrpc_client_base.AppStartError(
                '%s is installed on %s, but it is not instrumented.' %
                (self.package, self._serial))
        match = re.search(r'^instrumentation:(.*)\/(.*) \(target=(.*)\)$', out)
        target_name = match.group(3)
        # Check that the instrumentation target is installed if it's not the
        # same as the snippet package.
        if target_name != self.package:
            out = self._adb_grep_wrapper(
                r'pm list package | tr -d "\r" | grep ^package:%s$' %
                target_name)
            if not out:
                raise jsonrpc_client_base.AppStartError(
                    'Instrumentation target %s is not installed on %s' %
                    (target_name, self._serial))