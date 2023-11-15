    def map_data(self, cached=False):
        '''
        Create a data map of what to execute on
        '''
        ret = {'create': {}}
        pmap = self.map_providers_parallel(cached=cached)
        exist = set()
        defined = set()
        for profile_name, nodes in six.iteritems(self.rendered_map):
            if profile_name not in self.opts['profiles']:
                msg = (six.u(
                    'The required profile, {0!r}, defined in the map '
                    'does not exist. The defined nodes, {1}, will not '
                    'be created.').format(
                        profile_name,
                        ', '.join('{0!r}'.format(node) for node in nodes))
                )
                log.error(msg)
                if 'errors' not in ret:
                    ret['errors'] = {}
                ret['errors'][profile_name] = msg
                continue

            profile_data = self.opts['profiles'].get(profile_name)
            for nodename, overrides in six.iteritems(nodes):
                # Get the VM name
                nodedata = copy.deepcopy(profile_data)
                # Update profile data with the map overrides
                for setting in ('grains', 'master', 'minion', 'volumes',
                                'requires'):
                    deprecated = 'map_{0}'.format(setting)
                    if deprecated in overrides:
                        log.warn(six.u(
                            'The use of {0!r} on the {1!r} mapping has '
                            'been deprecated. The preferred way now is to '
                            'just define {2!r}. For now, salt-cloud will do '
                            'the proper thing and convert the deprecated '
                            'mapping into the preferred one.').format(
                                deprecated, nodename, setting
                            )
                        )
                        overrides[setting] = overrides.pop(deprecated)

                # merge minion grains from map file
                if 'minion' in overrides and \
                        'minion' in nodedata and \
                        'grains' in overrides['minion'] and \
                        'grains' in nodedata['minion']:
                    nodedata['minion']['grains'].update(
                        overrides['minion']['grains']
                    )
                    del overrides['minion']['grains']
                    # remove minion key if now is empty dict
                    if len(overrides['minion']) == 0:
                        del overrides['minion']

                nodedata.update(overrides)
                # Add the computed information to the return data
                ret['create'][nodename] = nodedata
                # Add the node name to the defined set
                alias, driver = nodedata['provider'].split(':')
                defined.add((alias, driver, nodename))

        def get_matching_by_name(name):
            matches = {}
            for alias, drivers in six.iteritems(pmap):
                for driver, vms in six.iteritems(drivers):
                    for vm_name, details in six.iteritems(vms):
                        if vm_name == name and driver not in matches:
                            matches[driver] = details['state']
            return matches

        for alias, drivers in six.iteritems(pmap):
            for driver, vms in six.iteritems(drivers):
                for name, details in six.iteritems(vms):
                    exist.add((alias, driver, name))
                    if name not in ret['create']:
                        continue

                    # The machine is set to be created. Does it already exist?
                    matching = get_matching_by_name(name)
                    if not matching:
                        continue

                    # A machine by the same name exists
                    for item in matching:
                        if name not in ret['create']:
                            # Machine already removed
                            break

                        log.warn(
                            six.u('{0!r} already exists, removing from '
                                  'the create map.').format(name))

                        if 'existing' not in ret:
                            ret['existing'] = {}
                        ret['existing'][name] = ret['create'].pop(name)

        if 'hard' in self.opts and self.opts['hard']:
            if self.opts['enable_hard_maps'] is False:
                raise SaltCloudSystemExit(
                    'The --hard map can be extremely dangerous to use, '
                    'and therefore must explicitly be enabled in the main '
                    'configuration file, by setting \'enable_hard_maps\' '
                    'to True'
                )

            # Hard maps are enabled, Look for the items to delete.
            ret['destroy'] = exist.difference(defined)
        return ret