    def add_port_to_if_grp(self):
        """
        adds port to a ifgrp
        """
        route_obj = netapp_utils.zapi.NaElement("net-port-ifgrp-add-port")
        route_obj.add_new_child("ifgrp-name", self.name)
        route_obj.add_new_child("port", self.port)
        route_obj.add_new_child("node", self.node)
        try:
            self.server.invoke_successfully(route_obj, True)
        except netapp_utils.zapi.NaApiError as error:
            self.module.fail_json(msg='Error adding port %s to if_group %s: %s' %
                                      (self.port, self.name, to_native(error)),
                                  exception=traceback.format_exc())