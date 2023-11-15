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
        if_group_info.add_new_child('port', self.parameters['name'])
        if_group_info.add_new_child('port-type', 'if_group')
        if_group_info.add_new_child('node', self.parameters['node'])
        query = netapp_utils.zapi.NaElement('query')
        query.add_child_elem(if_group_info)
        if_group_iter.add_child_elem(query)
        try:
            result = self.server.invoke_successfully(if_group_iter, True)
        except netapp_utils.zapi.NaApiError as error:
            self.module.fail_json(msg='Error getting if_group %s: %s' % (self.parameters['name'], to_native(error)),
                                  exception=traceback.format_exc())

        return_value = None

        if result.get_child_by_name('num-records') and int(result['num-records']) >= 1:
            if_group_attributes = result['attributes-list']['net-port-info']
            return_value = {
                'name': if_group_attributes['port'],
                'distribution_function': if_group_attributes['ifgrp-distribution-function'],
                'mode': if_group_attributes['ifgrp-mode'],
                'node': if_group_attributes['node'],
            }

        return return_value