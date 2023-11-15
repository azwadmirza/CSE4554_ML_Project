    def get_cpu_inventory(self):
        result = {}
        cpu_details = []
        cpu_list = []
        key = "Processors"

        # Search for 'key' entry and extract URI from it
        response = self.get_request(self.root_uri + self.systems_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        processors_uri = data[key]["@odata.id"]

        # Get a list of all CPUs and build respective URIs
        response = self.get_request(self.root_uri + processors_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        for cpu in data[u'Members']:
            cpu_list.append(cpu[u'@odata.id'])
        for c in cpu_list:
            uri = self.root_uri + c
            response = self.get_request(uri)
            if response['ret'] is False:
                return response
            data = response['data']
            cpu_details.append(dict(
                Name=data[u'Id'],
                Manufacturer=data[u'Manufacturer'],
                Model=data[u'Model'],
                MaxSpeedMHz=data[u'MaxSpeedMHz'],
                TotalCores=data[u'TotalCores'],
                TotalThreads=data[u'TotalThreads'],
                State=data[u'Status'][u'State'],
                Health=data[u'Status'][u'Health']))
        result["entries"] = cpu_details
        return result