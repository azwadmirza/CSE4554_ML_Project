    def apply_configuration_patches(self, old_version=None):
        """
        Override method.

        Apply any patch to configuration values on version changes.
        """
        self._update_defaults(self.defaults, old_version)

        if old_version and check_version(old_version, '44.1.0', '<'):
            run_lines = to_text_string(self.get('ipython_console',
                                                'startup/run_lines'))
            if run_lines is not NoDefault:
                run_lines = run_lines.replace(',', '; ')
                self.set('ipython_console', 'startup/run_lines', run_lines)