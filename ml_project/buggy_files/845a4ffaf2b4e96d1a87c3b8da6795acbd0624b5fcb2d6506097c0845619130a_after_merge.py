    def get_if_grp_ports(self):
        """
        Return ports of the if_group
        :param:
            name : Name of the if_group
        :return: Ports of the if_group. None if not found.
        :rtype: dict
        """
        if_group_iter = netapp_utils.zapi.NaElement('net-port-ifgrp-get')
        if_group_iter.add_new_child('ifgrp-name', self.parameters['name'])
        if_group_iter.add_new_child('node', self.parameters['node'])
        try:
            result = self.server.invoke_successfully(if_group_iter, True)
        except netapp_utils.zapi.NaApiError as error:
            self.module.fail_json(msg='Error getting if_group ports %s: %s' % (self.parameters['name'], to_native(error)),
                                  exception=traceback.format_exc())

        port_list = []
        if result.get_child_by_name('attributes'):
            if_group_attributes = result['attributes']['net-ifgrp-info']
            if if_group_attributes.get_child_by_name('ports'):
                ports = if_group_attributes.get_child_by_name('ports').get_children()
                for each in ports:
                    port_list.append(each.get_content())
        return {'ports': port_list}