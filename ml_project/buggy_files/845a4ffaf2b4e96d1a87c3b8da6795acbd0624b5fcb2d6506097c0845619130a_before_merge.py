    def get_if_grp_ports(self):
        """
        Return ports of the if_group
        :param:
            name : Name of the if_group

        :return: Ports of the if_group. None if not found.
        :rtype: dict
        """
        if_group_iter = netapp_utils.zapi.NaElement('net-port-ifgrp-get')
        if_group_iter.add_new_child('ifgrp-name', self.name)
        if_group_iter.add_new_child('node', self.node)
        result = self.server.invoke_successfully(if_group_iter, True)

        return_value = None

        if result.get_child_by_name('attributes'):
            if_group_attributes = result.get_child_by_name('attributes').get_child_by_name('net-ifgrp-info')
            name = if_group_attributes.get_child_content('ifgrp-name')
            mode = if_group_attributes.get_child_content('mode')
            port_list = []
            if if_group_attributes.get_child_by_name('ports'):
                ports = if_group_attributes.get_child_by_name('ports').get_children()
                for each in ports:
                    port_list.append(each.get_content())
            node = if_group_attributes.get_child_content('node')
            return_value = {
                'name': name,
                'mode': mode,
                'node': node,
                'ports': port_list
            }
        return return_value