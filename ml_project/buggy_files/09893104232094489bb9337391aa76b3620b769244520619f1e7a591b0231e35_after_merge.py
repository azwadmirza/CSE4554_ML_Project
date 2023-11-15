    def update_cache(self, scan_only_new_hosts=False):
        """Make calls to foreman and save the output in a cache"""

        self.groups = dict()
        self.hosts = dict()

        for host in self._get_hosts():
            if host['name'] in self.cache.keys() and scan_only_new_hosts:
                continue
            dns_name = host['name']

            host_data = self._get_host_data_by_id(host['id'])
            host_params = host_data.get('all_parameters', {})

            # Create ansible groups for hostgroup
            group = 'hostgroup'
            val = host.get('%s_title' % group) or host.get('%s_name' % group)
            if val:
                safe_key = self.to_safe('%s%s_%s' % (
                    to_text(self.group_prefix),
                    group,
                    to_text(val).lower()
                ))
                self.inventory[safe_key].append(dns_name)

            # Create ansible groups for environment, location and organization
            for group in ['environment', 'location', 'organization']:
                val = host.get('%s_name' % group)
                if val:
                    safe_key = self.to_safe('%s%s_%s' % (
                        to_text(self.group_prefix),
                        group,
                        to_text(val).lower()
                    ))
                    self.inventory[safe_key].append(dns_name)

            for group in ['lifecycle_environment', 'content_view']:
                val = host.get('content_facet_attributes', {}).get('%s_name' % group)
                if val:
                    safe_key = self.to_safe('%s%s_%s' % (
                        to_text(self.group_prefix),
                        group,
                        to_text(val).lower()
                    ))
                    self.inventory[safe_key].append(dns_name)

            params = self._resolve_params(host_params)

            # Ansible groups by parameters in host groups and Foreman host
            # attributes.
            groupby = dict()
            for k, v in params.items():
                groupby[k] = self.to_safe(to_text(v))

            # The name of the ansible groups is given by group_patterns:
            for pattern in self.group_patterns:
                try:
                    key = pattern.format(**groupby)
                    self.inventory[key].append(dns_name)
                except KeyError:
                    pass  # Host not part of this group

            if self.want_hostcollections:
                hostcollections = host_data.get('host_collections')

                if hostcollections:
                    # Create Ansible groups for host collections
                    for hostcollection in hostcollections:
                        safe_key = self.to_safe('%shostcollection_%s' % (self.group_prefix, hostcollection['name'].lower()))
                        self.inventory[safe_key].append(dns_name)

                self.hostcollections[dns_name] = hostcollections

            self.cache[dns_name] = host
            self.params[dns_name] = params
            self.facts[dns_name] = self._get_facts(host)
            self.inventory['all'].append(dns_name)
        self._write_cache()