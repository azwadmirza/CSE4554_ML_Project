    def set_one_time_boot_device(self, bootdevice, uefi_target, boot_next):
        result = {}
        key = "Boot"

        if not bootdevice:
            return {'ret': False,
                    'msg': "bootdevice option required for SetOneTimeBoot"}

        # Search for 'key' entry and extract URI from it
        response = self.get_request(self.root_uri + self.systems_uris[0])
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        if key not in data:
            return {'ret': False, 'msg': "Key %s not found" % key}

        boot = data[key]

        annotation = 'BootSourceOverrideTarget@Redfish.AllowableValues'
        if annotation in boot:
            allowable_values = boot[annotation]
            if isinstance(allowable_values, list) and bootdevice not in allowable_values:
                return {'ret': False,
                        'msg': "Boot device %s not in list of allowable values (%s)" %
                               (bootdevice, allowable_values)}

        # read existing values
        enabled = boot.get('BootSourceOverrideEnabled')
        target = boot.get('BootSourceOverrideTarget')
        cur_uefi_target = boot.get('UefiTargetBootSourceOverride')
        cur_boot_next = boot.get('BootNext')

        if bootdevice == 'UefiTarget':
            if not uefi_target:
                return {'ret': False,
                        'msg': "uefi_target option required to SetOneTimeBoot for UefiTarget"}
            if enabled == 'Once' and target == bootdevice and uefi_target == cur_uefi_target:
                # If properties are already set, no changes needed
                return {'ret': True, 'changed': False}
            payload = {
                'Boot': {
                    'BootSourceOverrideEnabled': 'Once',
                    'BootSourceOverrideTarget': bootdevice,
                    'UefiTargetBootSourceOverride': uefi_target
                }
            }
        elif bootdevice == 'UefiBootNext':
            if not boot_next:
                return {'ret': False,
                        'msg': "boot_next option required to SetOneTimeBoot for UefiBootNext"}
            if enabled == 'Once' and target == bootdevice and boot_next == cur_boot_next:
                # If properties are already set, no changes needed
                return {'ret': True, 'changed': False}
            payload = {
                'Boot': {
                    'BootSourceOverrideEnabled': 'Once',
                    'BootSourceOverrideTarget': bootdevice,
                    'BootNext': boot_next
                }
            }
        else:
            if enabled == 'Once' and target == bootdevice:
                # If properties are already set, no changes needed
                return {'ret': True, 'changed': False}
            payload = {
                'Boot': {
                    'BootSourceOverrideEnabled': 'Once',
                    'BootSourceOverrideTarget': bootdevice
                }
            }

        response = self.patch_request(self.root_uri + self.systems_uris[0], payload)
        if response['ret'] is False:
            return response
        return {'ret': True, 'changed': True}