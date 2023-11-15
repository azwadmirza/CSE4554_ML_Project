    def _populate_platform_instances(self):
        if self.molecule.args.get('platform'):
            if (len(
                (self.molecule.config.config['vagrant']['platforms']) > 1) and
                (self.molecule.args.get('platform') == 'all') and
                    not self._updated_multiplatform):
                new_instances = []

                for instance in self.molecule.config.config['vagrant'][
                        'instances']:
                    for platform in self.molecule.config.config['vagrant'][
                            'platforms']:
                        platform_instance = copy.deepcopy(instance)
                        platform_instance['platform'] = platform['box']
                        platform_instance['name'] = instance[
                            'name'] + '-' + platform['name']
                        platform_instance['vm_name'] = instance[
                            'name'] + '-' + platform['name']
                        new_instances.append(platform_instance)

                self.molecule.config.config['vagrant'][
                    'instances'] = new_instances
                self._updated_multiplatform = True