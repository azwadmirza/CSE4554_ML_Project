    def exec_module(self, **kwargs):

        for key in list(self.module_arg_spec.keys()) + ['tags']:
            setattr(self, key, kwargs[key])

        self.results['check_mode'] = self.check_mode

        resource_group = self.get_resource_group(self.resource_group)
        if not self.location:
            # Set default location
            self.location = resource_group.location

        if self.state == 'present' and self.purge_address_prefixes:
            for prefix in self.address_prefixes_cidr:
                if not CIDR_PATTERN.match(prefix):
                    self.fail("Parameter error: invalid address prefix value {0}".format(prefix))

            if self.dns_servers and len(self.dns_servers) > 2:
                self.fail("Parameter error: You can provide a maximum of 2 DNS servers.")

        changed = False
        results = dict()

        try:
            self.log('Fetching vnet {0}'.format(self.name))
            vnet = self.network_client.virtual_networks.get(self.resource_group, self.name)

            results = virtual_network_to_dict(vnet)
            self.log('Vnet exists {0}'.format(self.name))
            self.log(results, pretty_print=True)
            self.check_provisioning_state(vnet, self.state)

            if self.state == 'present':
                if self.address_prefixes_cidr:
                    existing_address_prefix_set = set(vnet.address_space.address_prefixes)
                    requested_address_prefix_set = set(self.address_prefixes_cidr)
                    missing_prefixes = requested_address_prefix_set - existing_address_prefix_set
                    extra_prefixes = existing_address_prefix_set - requested_address_prefix_set
                    if len(missing_prefixes) > 0:
                        self.log('CHANGED: there are missing address_prefixes')
                        changed = True
                        if not self.purge_address_prefixes:
                            # add the missing prefixes
                            for prefix in missing_prefixes:
                                results['address_prefixes'].append(prefix)

                    if len(extra_prefixes) > 0 and self.purge_address_prefixes:
                        self.log('CHANGED: there are address_prefixes to purge')
                        changed = True
                        # replace existing address prefixes with requested set
                        results['address_prefixes'] = self.address_prefixes_cidr

                update_tags, results['tags'] = self.update_tags(results['tags'])
                if update_tags:
                    changed = True

                if self.dns_servers:
                    existing_dns_set = set(vnet.dhcp_options.dns_servers)
                    requested_dns_set = set(self.dns_servers)
                    if existing_dns_set != requested_dns_set:
                        self.log('CHANGED: replacing DNS servers')
                        changed = True
                        results['dns_servers'] = self.dns_servers

                if self.purge_dns_servers and vnet.dhcp_options and len(vnet.dhcp_options.dns_servers) > 0:
                    self.log('CHANGED: purging existing DNS servers')
                    changed = True
                    results['dns_servers'] = []
            elif self.state == 'absent':
                self.log("CHANGED: vnet exists but requested state is 'absent'")
                changed = True
        except CloudError:
            self.log('Vnet {0} does not exist'.format(self.name))
            if self.state == 'present':
                self.log("CHANGED: vnet {0} does not exist but requested state is 'present'".format(self.name))
                changed = True

        self.results['changed'] = changed
        self.results['state'] = results

        if self.check_mode:
            return self.results

        if changed:
            if self.state == 'present':
                if not results:
                    # create a new virtual network
                    self.log("Create virtual network {0}".format(self.name))
                    if not self.address_prefixes_cidr:
                        self.fail('Parameter error: address_prefixes_cidr required when creating a virtual network')
                    vnet = self.network_models.VirtualNetwork(
                        location=self.location,
                        address_space=self.network_models.AddressSpace(
                            address_prefixes=self.address_prefixes_cidr
                        )
                    )
                    if self.dns_servers:
                        vnet.dhcp_options = self.network_models.DhcpOptions(
                            dns_servers=self.dns_servers
                        )
                    if self.tags:
                        vnet.tags = self.tags
                    self.results['state'] = self.create_or_update_vnet(vnet)
                else:
                    # update existing virtual network
                    self.log("Update virtual network {0}".format(self.name))
                    vnet = self.network_models.VirtualNetwork(
                        location=results['location'],
                        address_space=self.network_models.AddressSpace(
                            address_prefixes=results['address_prefixes']
                        ),
                        tags=results['tags']
                    )
                    if results.get('dns_servers'):
                        vnet.dhcp_options = self.network_models.DhcpOptions(
                            dns_servers=results['dns_servers']
                        )
                    self.results['state'] = self.create_or_update_vnet(vnet)
            elif self.state == 'absent':
                self.delete_virtual_network()
                self.results['state']['status'] = 'Deleted'

        return self.results