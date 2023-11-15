    def get_psu_inventory(self):
        result = {}
        psu_details = []
        psu_list = []

        # Get a list of all PSUs and build respective URIs
        response = self.get_request(self.root_uri + self.systems_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        for psu in data[u'Links'][u'PoweredBy']:
            psu_list.append(psu[u'@odata.id'])

        for p in psu_list:
            uri = self.root_uri + p
            response = self.get_request(uri)
            if response['ret'] is False:
                return response

            result['ret'] = True
            data = response['data']

            psu = {}
            psu['Name'] = data[u'Name']
            psu['Model'] = data[u'Model']
            psu['SerialNumber'] = data[u'SerialNumber']
            psu['PartNumber'] = data[u'PartNumber']
            if 'Manufacturer' in data:   # not available in all generations
                psu['Manufacturer'] = data[u'Manufacturer']
            psu['FirmwareVersion'] = data[u'FirmwareVersion']
            psu['PowerCapacityWatts'] = data[u'PowerCapacityWatts']
            psu['PowerSupplyType'] = data[u'PowerSupplyType']
            psu['Status'] = data[u'Status'][u'State']
            psu['Health'] = data[u'Status'][u'Health']
            psu_details.append(psu)
        result["entries"] = psu_details
        return result