    def inject_ovf_env(self):
        attrib = {
            'xmlns': 'http://schemas.dmtf.org/ovf/environment/1',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xmlns:oe': 'http://schemas.dmtf.org/ovf/environment/1',
            'xmlns:ve': 'http://www.vmware.com/schema/ovfenv',
            'oe:id': '',
            've:esxId': self.entity._moId
        }
        env = ET.Element('Environment', **attrib)

        platform = ET.SubElement(env, 'PlatformSection')
        ET.SubElement(platform, 'Kind').text = self.si.about.name
        ET.SubElement(platform, 'Version').text = self.si.about.version
        ET.SubElement(platform, 'Vendor').text = self.si.about.vendor
        ET.SubElement(platform, 'Locale').text = 'US'

        prop_section = ET.SubElement(env, 'PropertySection')
        for key, value in self.params['properties'].items():
            params = {
                'oe:key': key,
                'oe:value': str(value) if isinstance(value, bool) else value
            }
            ET.SubElement(prop_section, 'Property', **params)

        opt = vim.option.OptionValue()
        opt.key = 'guestinfo.ovfEnv'
        opt.value = '<?xml version="1.0" encoding="UTF-8"?>' + to_native(ET.tostring(env))

        config_spec = vim.vm.ConfigSpec()
        config_spec.extraConfig = [opt]

        task = self.entity.ReconfigVM_Task(config_spec)
        wait_for_task(task)