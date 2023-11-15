    def get_config(self, source='running', format='text', flags=None):
        if source not in ['running']:
            raise ValueError("fetching configuration from %s is not supported" % source)

        lookup = {'running': 'running-config'}

        cmd = 'show {0} '.format(lookup[source])
        cmd += ' '.join(to_list(flags))
        cmd = cmd.strip()

        return self.send_command(cmd)