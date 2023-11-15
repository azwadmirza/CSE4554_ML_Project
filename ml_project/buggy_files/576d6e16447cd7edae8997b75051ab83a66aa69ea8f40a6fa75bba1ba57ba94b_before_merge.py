    def is_package_installed(self, package):
        """Check if package is installed."""
        out = self.adb_command(['pm', 'list', 'packages'], True)
        pkg = f'{package}'.encode('utf-8')
        if pkg + b'\n' in out or pkg + b'\r\n' in out:
            # Windows uses \r\n
            return True
        return False