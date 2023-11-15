    def _mount_references(self):
        '''
        Find the references that is defined in self.configuration
        :return:
        '''
        self.resources_raw = deepcopy(self.resources)
        invalid_references = ('var.', 'each.')

        # This section will link resources found in configuration part of the plan output.
        # The reference should be on both ways (A->B, B->A) since terraform sometimes report these references
        # in opposite ways, depending on the provider structure.
        for resource in self.configuration['resources']:
            if 'expressions' in self.configuration['resources'][resource]:
                ref_list = {}
                for key, value in self.configuration['resources'][resource]['expressions'].items():
                    references = seek_key_in_dict(value, 'references') if isinstance(value, (dict, list)) else []

                    valid_references = []
                    for ref in references:
                        if isinstance(ref, dict) and ref.get('references'):
                            valid_references = [r for r in ref['references'] if not r.startswith(invalid_references)]

                    for ref in valid_references:
                        if key not in ref_list:
                            ref_list[key] = self._find_resource_from_name(ref)
                        else:
                            ref_list[key].extend(self._find_resource_from_name(ref))

                    # This is where we synchronise constant_value in the configuration section with the resource
                    # for filling up the missing elements that hasn't been defined in the resource due to provider
                    # implementation.
                    target_resource = [t for t in [self.resources.get(resource, {}).get('address')] if t is not None]
                    if not target_resource:
                        target_resource = [k for k in self.resources.keys() if k.startswith(resource)]

                    for t_r in target_resource:
                        if type(value) is type(self.resources[t_r]['values'].get(key)) and self.resources[t_r]['values'].get(key) != value:
                            if isinstance(value, (list, dict)):
                                merge_dicts(self.resources[t_r]['values'][key], value)

                if ref_list:
                    ref_type = self.configuration['resources'][resource]['expressions'].get('type', {})

                    if 'references' in ref_type:
                        ref_type = resource.split('.')[0]

                    if not ref_type and not self.is_type(resource, 'data'):
                        resource_type, resource_id = resource.split('.')
                        ref_type = resource_type

                    for k, v in ref_list.items():
                        v = flatten_list(v)

                    # Mounting A->B
                    source_resources = self._find_resource_from_name(self.configuration['resources'][resource]['address'])
                    self._mount_resources(source=source_resources,
                                          target=ref_list,
                                          ref_type=ref_type)
                    
                    # Mounting B->A
                    for parameter, target_resources in ref_list.items():
                        for target_resource in target_resources:
                            if not self.is_type(resource, 'data') and not self.is_type(resource, 'var') and not self.is_type(resource, 'provider'):
                                ref_type = target_resource.split('.', maxsplit=1)[0]

                                self._mount_resources(source=[target_resource],
                                                      target={parameter: source_resources},
                                                      ref_type=ref_type)