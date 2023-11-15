    def get_nic_inventory(self):
        result = {}
        nic_details = []
        nic_list = []
        key = "EthernetInterfaces"

        # Search for 'key' entry and extract URI from it
        response = self.get_request(self.root_uri + self.systems_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

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

            nic['Name'] = data[u'Name']
            nic['FQDN'] = data[u'FQDN']
            for d in data[u'IPv4Addresses']:
                nic['IPv4'] = d[u'Address']
                if 'GateWay' in d:   # not always available
                    nic['Gateway'] = d[u'GateWay']
                nic['SubnetMask'] = d[u'SubnetMask']
            for d in data[u'IPv6Addresses']:
                nic['IPv6'] = d[u'Address']
            for d in data[u'NameServers']:
                nic['NameServers'] = d
            nic['MACAddress'] = data[u'PermanentMACAddress']
            nic['SpeedMbps'] = data[u'SpeedMbps']
            nic['MTU'] = data[u'MTUSize']
            nic['AutoNeg'] = data[u'AutoNeg']
            if 'Status' in data:    # not available when power is off
                nic['Health'] = data[u'Status'][u'Health']
                nic['State'] = data[u'Status'][u'State']
            nic_details.append(nic)
        result["entries"] = nic_details
        return result