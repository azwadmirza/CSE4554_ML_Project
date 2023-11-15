    def update_cache(self):
        """ Make calls to cobbler and save the output in a cache """

        self._connect()
        self.groups = dict()
        self.hosts = dict()
        if self.token is not None:
            data = self.conn.get_systems(self.token)
        else:
            data = self.conn.get_systems()

        for host in data:
            # Get the FQDN for the host and add it to the right groups
            dns_name = host['hostname']  # None
            ksmeta = None
            interfaces = host['interfaces']
            # hostname is often empty for non-static IP hosts
            if dns_name == '':
                for (iname, ivalue) in iteritems(interfaces):
                    if ivalue['management'] or not ivalue['static']:
                        this_dns_name = ivalue.get('dns_name', None)
                        if this_dns_name is not None and this_dns_name is not "":
                            dns_name = this_dns_name

            if dns_name == '':
                continue

            status = host['status']
            profile = host['profile']
            classes = host[orderby_keyname]

            if status not in self.inventory:
                self.inventory[status] = []
            self.inventory[status].append(dns_name)

            if profile not in self.inventory:
                self.inventory[profile] = []
            self.inventory[profile].append(dns_name)

            for cls in classes:
                if cls not in self.inventory:
                    self.inventory[cls] = []
                self.inventory[cls].append(dns_name)

            # Since we already have all of the data for the host, update the host details as well

            # The old way was ksmeta only -- provide backwards compatibility

            self.cache[dns_name] = host
            if "ks_meta" in host:
                for key, value in iteritems(host["ks_meta"]):
                    self.cache[dns_name][key] = value

        self.write_to_cache(self.cache, self.cache_path_cache)
        self.write_to_cache(self.inventory, self.cache_path_inventory)