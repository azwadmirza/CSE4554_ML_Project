    def get_bios_boot_order(self):
        result = {}
        boot_device_list = []
        boot_device_details = []
        key = "Bios"
        bootsources = "BootSources"

        # Search for 'key' entry and extract URI from it
        response = self.get_request(self.root_uri + self.systems_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']
        bios_uri = data[key]["@odata.id"]

        # Get boot mode first as it will determine what attribute to read
        response = self.get_request(self.root_uri + bios_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        boot_mode = data[u'Attributes']["BootMode"]
        if boot_mode == "Uefi":
            boot_seq = "UefiBootSeq"
        else:
            boot_seq = "BootSeq"

        response = self.get_request(self.root_uri + self.systems_uri + "/" + bootsources)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        boot_device_list = data[u'Attributes'][boot_seq]
        for b in boot_device_list:
            boot_device = {}
            boot_device["Index"] = b[u'Index']
            boot_device["Name"] = b[u'Name']
            boot_device["Enabled"] = b[u'Enabled']
            boot_device_details.append(boot_device)
        result["entries"] = boot_device_details
        return result