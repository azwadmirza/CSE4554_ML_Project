    def build_data_dir(self):
        """
        Returns the path of the OnionShare data directory.
        """
        if self.platform == 'Windows':
            try:
                appdata = os.environ['APPDATA']
                onionshare_data_dir = '{}\\OnionShare'.format(appdata)
            except:
                # If for some reason we don't have the 'APPDATA' environment variable
                # (like running tests in Linux while pretending to be in Windows)
                onionshare_data_dir = '~/.config/onionshare'
        elif self.platform == 'Darwin':
            onionshare_data_dir = '~/Library/Application Support/OnionShare'
        else:
            onionshare_data_dir = '~/.config/onionshare'

        os.makedirs(onionshare_data_dir, 0o700, True)
        return onionshare_data_dir