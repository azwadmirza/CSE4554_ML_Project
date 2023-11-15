    def get_if_grp(self):
        """
        Return details about the if_group
        :param:
            name : Name of the if_group

        :return: Details about the if_group. None if not found.
        :rtype: dict
        """
        if_group_iter = netapp_utils.zapi.NaElement('net-port-get-iter')
        if_group_info = netapp_utils.zapi.NaElement('net-port-info')
        if_group_info.add_new_child('port', self.name)
        if_group_info.add_new_child('port-type', 'if_group')
        query = netapp_utils.zapi.NaElement('query')
        query.add_child_elem(if_group_info)
        if_group_iter.add_child_elem(query)
        result = self.server.invoke_successfully(if_group_iter, True)

        return_value = None

        if result.get_child_by_name('num-records') and \
                int(result.get_child_content('num-records')) >= 1:

            if_group_attributes = result.get_child_by_name('attributes-list').get_child_by_name('net-port-info')
            distribution_function = if_group_attributes.get_child_content('ifgrp-distribution-function')
            name = if_group_attributes.get_child_content('port')
            mode = if_group_attributes.get_child_content('ifgrp-mode')
            ports = if_group_attributes.get_child_content('ifgrp-port')
            node = if_group_attributes.get_child_content('node')

            return_value = {
                'name': name,
                'distribution_function': distribution_function,
                'mode': mode,
                'node': node,
                'ports': ports
            }

        return return_value