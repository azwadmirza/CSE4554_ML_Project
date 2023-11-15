    def _get_driver_name(self):
        driver = self.args.get('driver')
        if driver:
            return driver
        elif self.config.config.get('driver'):
            return self.config.config['driver'].get('name')
        elif 'vagrant' in self.config.config:
            return 'vagrant'
        elif 'docker' in self.config.config:
            return 'docker'
        elif 'openstack' in self.config.config:
            return 'openstack'