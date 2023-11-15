    def create_if_grp(self):
        """
        Creates a new ifgrp
        """
        route_obj = netapp_utils.zapi.NaElement("net-port-ifgrp-create")
        route_obj.add_new_child("distribution-function", self.distribution_function)
        route_obj.add_new_child("ifgrp-name", self.name)
        route_obj.add_new_child("mode", self.mode)
        route_obj.add_new_child("node", self.node)
        try:
            self.server.invoke_successfully(route_obj, True)
        except netapp_utils.zapi.NaApiError as error:
            self.module.fail_json(msg='Error creating if_group %s: %s' % (self.name, to_native(error)),
                                  exception=traceback.format_exc())