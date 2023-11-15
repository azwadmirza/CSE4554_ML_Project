    def build_data_dir(self):
        """
        Returns the path of the OnionShare data directory.
        """
        if self.platform == 'Windows':
            try:
                appdata = os.environ['APPDATA']
                return '{}\\OnionShare'.format(appdata)
            except:
                # If for some reason we don't have the 'APPDATA' environment variable
                # (like running tests in Linux while pretending to be in Windows)
                return os.path.expanduser('~/.config/onionshare')
        elif self.platform == 'Darwin':
            return os.path.expanduser('~/Library/Application Support/OnionShare')
        else:
            return os.path.expanduser('~/.config/onionshare')