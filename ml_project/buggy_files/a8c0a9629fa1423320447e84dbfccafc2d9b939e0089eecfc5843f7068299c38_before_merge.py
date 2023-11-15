    def set_one_time_boot_device(self, bootdevice):
        result = {}
        key = "Bios"

        # Search for 'key' entry and extract URI from it
        response = self.get_request(self.root_uri + self.systems_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']
        bios_uri = data[key]["@odata.id"]

        response = self.get_request(self.root_uri + bios_uri)
        if response['ret'] is False:
            return response
        data = response['data']

        boot_mode = data[u'Attributes']["BootMode"]
        if boot_mode == "Uefi":
            payload = {"Boot": {"BootSourceOverrideTarget": "UefiTarget", "UefiTargetBootSourceOverride": bootdevice}}
        else:
            payload = {"Boot": {"BootSourceOverrideTarget": bootdevice}}

        response = self.patch_request(self.root_uri + self.systems_uri, payload, HEADERS)
        if response['ret'] is False:
            return response
        return {'ret': True}