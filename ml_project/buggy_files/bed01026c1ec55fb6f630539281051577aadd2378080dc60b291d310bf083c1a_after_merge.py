    def remove_port_to_if_grp(self, port):
        """
        removes port from a ifgrp
        """
        route_obj = netapp_utils.zapi.NaElement("net-port-ifgrp-remove-port")
        route_obj.add_new_child("ifgrp-name", self.parameters['name'])
        route_obj.add_new_child("port", port)
        route_obj.add_new_child("node", self.parameters['node'])
        try:
            self.server.invoke_successfully(route_obj, True)
        except netapp_utils.zapi.NaApiError as error:
            self.module.fail_json(msg='Error removing port %s to if_group %s: %s' %
                                      (port, self.parameters['name'], to_native(error)),
                                  exception=traceback.format_exc())