    def get_disk_inventory(self):
        result = {}
        disks_details = []
        controller_list = []

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
                disks_details.append(dict(
                    Controller=data[u'Name'],
                    Name=device[u'Name'],
                    Manufacturer=device[u'Manufacturer'],
                    Model=device[u'Model'],
                    State=device[u'Status'][u'State'],
                    Health=device[u'Status'][u'Health']))
        result["entries"] = disks_details
        return result