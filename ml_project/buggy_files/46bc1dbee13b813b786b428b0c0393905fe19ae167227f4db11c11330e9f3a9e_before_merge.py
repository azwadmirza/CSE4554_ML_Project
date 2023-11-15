    def do_action(self, names, kwargs):
        '''
        Perform an action on a VM which may be specific to this cloud provider
        '''
        ret = {}
        invalid_functions = {}
        names = set(names)

        for alias, drivers in six.iteritems(self.map_providers_parallel()):
            if not names:
                break
            for driver, vms in six.iteritems(drivers):
                if not names:
                    break
                valid_function = True
                fun = '{0}.{1}'.format(driver, self.opts['action'])
                if fun not in self.clouds:
                    log.info(
                        '\'{0}()\' is not available. Not actioning...'.format(
                            fun
                        )
                    )
                    valid_function = False
                for vm_name, vm_details in six.iteritems(vms):
                    if not names:
                        break
                    if vm_name not in names:
                        if not isinstance(vm_details, dict):
                            vm_details = {}
                        if 'id' in vm_details and vm_details['id'] in names:
                            vm_name = vm_details['id']
                        else:
                            log.debug(
                                'vm:{0} in provider:{1} is not in name '
                                'list:\'{2}\''.format(vm_name, driver, names)
                            )
                            continue

                    # Build the dictionary of invalid functions with their associated VMs.
                    if valid_function is False:
                        if invalid_functions.get(fun) is None:
                            invalid_functions.update({fun: []})
                        invalid_functions[fun].append(vm_name)
                        continue

                    with context.func_globals_inject(
                        self.clouds[fun],
                        __active_provider_name__=':'.join([alias, driver])
                    ):
                        if alias not in ret:
                            ret[alias] = {}
                        if driver not in ret[alias]:
                            ret[alias][driver] = {}

                        # Clean kwargs of "__pub_*" data before running the cloud action call.
                        # Prevents calling positional "kwarg" arg before "call" when no kwarg
                        # argument is present in the cloud driver function's arg spec.
                        kwargs = salt.utils.clean_kwargs(**kwargs)

                        if kwargs:
                            ret[alias][driver][vm_name] = self.clouds[fun](
                                vm_name, kwargs, call='action'
                            )
                        else:
                            ret[alias][driver][vm_name] = self.clouds[fun](
                                vm_name, call='action'
                            )
                        names.remove(vm_name)

        # Set the return information for the VMs listed in the invalid_functions dict.
        missing_vms = set()
        if invalid_functions:
            ret['Invalid Actions'] = invalid_functions
            invalid_func_vms = set()
            for key, val in six.iteritems(invalid_functions):
                invalid_func_vms = invalid_func_vms.union(set(val))

            # Find the VMs that are in names, but not in set of invalid functions.
            missing_vms = names.difference(invalid_func_vms)
            if missing_vms:
                ret['Not Found'] = list(missing_vms)
                ret['Not Actioned/Not Running'] = list(names)

        if not names:
            return ret

        # Don't return missing VM information for invalid functions until after we've had a
        # Chance to return successful actions. If a function is valid for one driver, but
        # Not another, we want to make sure the successful action is returned properly.
        if missing_vms:
            return ret

        # If we reach this point, the Not Actioned and Not Found lists will be the same,
        # But we want to list both for clarity/consistency with the invalid functions lists.
        ret['Not Actioned/Not Running'] = list(names)
        ret['Not Found'] = list(names)
        return ret