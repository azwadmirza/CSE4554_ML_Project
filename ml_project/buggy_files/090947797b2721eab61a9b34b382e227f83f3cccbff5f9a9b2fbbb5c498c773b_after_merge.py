    def get_device_info(self):
        device_info = dict()
        device_info['network_os'] = 'junos'
        ele = new_ele('get-software-information')
        data = self.execute_rpc(to_xml(ele))
        reply = to_ele(data)
        sw_info = reply.find('.//software-information')

        device_info['network_os_version'] = self.get_text(sw_info, 'junos-version')
        device_info['network_os_hostname'] = self.get_text(sw_info, 'host-name')
        device_info['network_os_model'] = self.get_text(sw_info, 'product-model')

        return device_info