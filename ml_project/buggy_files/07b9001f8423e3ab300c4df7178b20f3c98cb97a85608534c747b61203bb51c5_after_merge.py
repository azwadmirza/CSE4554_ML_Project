    def get_nic_inventory(self):
        result = {}
        nic_list = []
        nic_results = []
        key = "EthernetInterfaces"
        # Get these entries, but does not fail if not found
        properties = ['Description', 'FQDN', 'IPv4Addresses', 'IPv6Addresses',
                      'NameServers', 'PermanentMACAddress', 'SpeedMbps', 'MTUSize',
                      'AutoNeg', 'Status']

        # Search for 'key' entry and extract URI from it
        response = self.get_request(self.root_uri + self.systems_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        if key not in data:
            return {'ret': False, 'msg': "Key %s not found" % key}

        ethernetinterfaces_uri = data[key]["@odata.id"]

        # Get a list of all network controllers and build respective URIs
        response = self.get_request(self.root_uri + ethernetinterfaces_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        for nic in data[u'Members']:
            nic_list.append(nic[u'@odata.id'])

        for n in nic_list:
            nic = {}
            uri = self.root_uri + n
            response = self.get_request(uri)
            if response['ret'] is False:
                return response
            data = response['data']

            for property in properties:
                if property in data:
                    nic[property] = data[property]

            nic_results.append(nic)
        result["entries"] = nic_results
        return result