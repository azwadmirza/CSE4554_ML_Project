    def _mount_resources(self, source, target, ref_type):
        '''
        Mounts values of the source resource to the target resource's values with ref_type key

        :param source: source resource
        :param target:  target resource
        :param ref_type: reference type (e.g. ingress )
        :return: none
        '''
        for source_resource in source:
            for target_resource in target:
                if ref_type not in self.resources[target_resource]['values']:
                    self.resources[target_resource]['values'][ref_type] = list()
                    self.resources[target_resource]['values'][ref_type].append(self.resources[source_resource]['values'])
                else:
                    self.resources[target_resource]['values'][ref_type].append(self.resources[source_resource]['values'])