    def get_config(self, source='running', format='text', filter=None):
        lookup = {'running': 'running-config'}
        if source not in lookup:
            return self.invalid_params("fetching configuration from %s is not supported" % source)
        if filter:
            cmd = 'show {0} {1}'.format(lookup[source], filter)
        else:
            cmd = 'show {0}'.format(lookup[source])

        return self.send_command(cmd)