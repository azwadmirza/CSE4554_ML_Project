    def delete_if_grp(self):
        """
        Deletes a ifgrp
        """
        route_obj = netapp_utils.zapi.NaElement("net-port-ifgrp-destroy")
        route_obj.add_new_child("ifgrp-name", self.name)
        route_obj.add_new_child("node", self.node)
        try:
            self.server.invoke_successfully(route_obj, True)
        except netapp_utils.zapi.NaApiError as error:
            self.module.fail_json(msg='Error deleting if_group %s: %s' % (self.name, to_native(error)),
                                  exception=traceback.format_exc())