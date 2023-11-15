    def get_disk_inventory(self):
        result = {}
        controller_list = []
        disk_results = []
        # Get these entries, but does not fail if not found
        properties = ['Name', 'Manufacturer', 'Model', 'Status', 'CapacityBytes']

        # Find Storage service
        response = self.get_request(self.root_uri + self.systems_uri)
        if response['ret'] is False:
            return response
        data = response['data']

        if 'SimpleStorage' not in data:
            return {'ret': False, 'msg': "SimpleStorage resource not found"}

        # Get a list of all storage controllers and build respective URIs
        storage_uri = data["SimpleStorage"]["@odata.id"]
        response = self.get_request(self.root_uri + storage_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        for controller in data[u'Members']:
            controller_list.append(controller[u'@odata.id'])

        for c in controller_list:
            uri = self.root_uri + c
            response = self.get_request(uri)
            if response['ret'] is False:
                return response
            data = response['data']

            for device in data[u'Devices']:
                disk = {}
                for property in properties:
                    if property in device:
                        disk[property] = device[property]
                disk_results.append(disk)
        result["entries"] = disk_results
        return result