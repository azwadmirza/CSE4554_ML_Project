    def get_system_inventory(self):
        result = {}
        inventory = {}
        response = self.get_request(self.root_uri + self.systems_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        # There could be more information to extract
        inventory['Status'] = data[u'Status'][u'Health']
        inventory['HostName'] = data[u'HostName']
        inventory['PowerState'] = data[u'PowerState']
        inventory['Model'] = data[u'Model']
        inventory['Manufacturer'] = data[u'Manufacturer']
        inventory['PartNumber'] = data[u'PartNumber']
        inventory['SystemType'] = data[u'SystemType']
        inventory['AssetTag'] = data[u'AssetTag']
        inventory['ServiceTag'] = data[u'SKU']
        inventory['SerialNumber'] = data[u'SerialNumber']
        inventory['BiosVersion'] = data[u'BiosVersion']
        inventory['MemoryTotal'] = data[u'MemorySummary'][u'TotalSystemMemoryGiB']
        inventory['MemoryHealth'] = data[u'MemorySummary'][u'Status'][u'Health']
        inventory['CpuCount'] = data[u'ProcessorSummary'][u'Count']
        inventory['CpuModel'] = data[u'ProcessorSummary'][u'Model']
        inventory['CpuHealth'] = data[u'ProcessorSummary'][u'Status'][u'Health']

        datadict = data[u'Boot']
        if 'BootSourceOverrideMode' in datadict.keys():
            inventory['BootSourceOverrideMode'] = data[u'Boot'][u'BootSourceOverrideMode']
        else:
            # Not available in earlier server generations
            inventory['BootSourceOverrideMode'] = "Not available"

        if 'TrustedModules' in data:
            for d in data[u'TrustedModules']:
                if 'InterfaceType' in d.keys():
                    inventory['TPMInterfaceType'] = d[u'InterfaceType']
                inventory['TPMStatus'] = d[u'Status'][u'State']
        else:
            # Not available in earlier server generations
            inventory['TPMInterfaceType'] = "Not available"
            inventory['TPMStatus'] = "Not available"

        result["entries"] = inventory
        return result