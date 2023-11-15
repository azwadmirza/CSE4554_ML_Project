    def install_apk(self, apk_path, package):
        """Install APK and Verify Installation."""
        if self.is_package_installed(package, ''):
            logger.info('Removing existing installation')
            # Remove existing installation'
            self.adb_command(['uninstall', package], False, True)
        # Disable install verification
        self.adb_command([
            'settings',
            'put',
            'global',
            'verifier_verify_adb_installs',
            '0',
        ], True)
        logger.info('Installing APK')
        # Install APK
        out = self.adb_command([
            'install',
            '-r',
            '-t',
            '-d',
            apk_path], False, True)
        if not out:
            return False, 'adb install failed'
        out = out.decode('utf-8', 'ignore')
        # Verify Installation
        return self.is_package_installed(package, out), out