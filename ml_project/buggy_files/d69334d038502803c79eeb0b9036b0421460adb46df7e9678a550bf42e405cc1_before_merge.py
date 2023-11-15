    def map_data(self, cached=False):
        '''
        Create a data map of what to execute on
        '''
        ret = {'create': {}}
        pmap = self.map_providers_parallel(cached=cached)
        exist = set()
        defined = set()
        for profile_name, nodes in self.rendered_map.items():
            if profile_name not in self.opts['profiles']:
                msg = (
                    'The required profile, {0!r}, defined in the map '
                    'does not exist. The defined nodes, {1}, will not '
                    'be created.'.format(
                        profile_name,
                        ', '.join('{0!r}'.format(node) for node in nodes)
                    )
                )
                log.error(msg)
                if 'errors' not in ret:
                    ret['errors'] = {}
                ret['errors'][profile_name] = msg
                continue

            profile_data = self.opts['profiles'].get(profile_name)
            for nodename, overrides in nodes.items():
                # Get the VM name
                nodedata = copy.deepcopy(profile_data)
                # Update profile data with the map overrides
                for setting in ('grains', 'master', 'minion', 'volumes',
                                'requires'):
                    deprecated = 'map_{0}'.format(setting)
                    if deprecated in overrides:
                        log.warn(
                            'The use of {0!r} on the {1!r} mapping has '
                            'been deprecated. The preferred way now is to '
                            'just define {2!r}. For now, salt-cloud will do '
                            'the proper thing and convert the deprecated '
                            'mapping into the preferred one.'.format(
                                deprecated, nodename, setting
                            )
                        )
                        overrides[setting] = overrides.pop(deprecated)

                # merge minion grains from map file
                if 'minion' in overrides and 'minion' in nodedata:
                    if 'grains' in overrides['minion']:
                        if 'grains' in nodedata['minion']:
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
            for alias, drivers in pmap.items():
                for driver, vms in drivers.items():
                    for vm_name, details in vms.items():
                        if vm_name == name:
                            if driver not in matches:
                                matches[driver] = details['state']
            return matches

        for alias, drivers in pmap.items():
            for driver, vms in drivers.items():
                for name, details in vms.items():
                    exist.add((alias, driver, name))
                    if name not in ret['create']:
                        continue

                    # The machine is set to be created. Does it already exist?
                    matching = get_matching_by_name(name)
                    if not matching:
                        continue

                    # A machine by the same name exists
                    for mdriver, state in matching.items():
                        if name not in ret['create']:
                            # Machine already removed
                            break

                        if mdriver not in ('aws', 'ec2') and \
                                state.lower() != 'terminated':
                            # Regarding other providers, simply remove
                            # them for the create map.
                            log.warn(
                                '{0!r} already exists, removing from '
                                'the create map'.format(name)
                            )
                            if 'existing' not in ret:
                                ret['existing'] = {}
                            ret['existing'][name] = ret['create'].pop(name)
                            continue

                        if state.lower() != 'terminated':
                            log.info(
                                '{0!r} already exists, removing '
                                'from the create map'.format(name)
                            )
                            if 'existing' not in ret:
                                ret['existing'] = {}
                            ret['existing'][name] = ret['create'].pop(name)

        if self.opts['hard']:
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