    def apply(self):
        changed = False
        ifgroup_exists = False
        add_ports_exists = True
        remove_ports_exists = False
        results = netapp_utils.get_cserver(self.server)
        cserver = netapp_utils.setup_na_ontap_zapi(module=self.module, vserver=results)
        netapp_utils.ems_log_event("na_ontap_net_ifgrp", cserver)
        if_group_detail = self.get_if_grp()
        if if_group_detail:
            ifgroup_exists = True
            ifgrp_ports_detail = self.get_if_grp_ports()
            if self.state == 'absent':
                changed = True
                if self.port:
                    if self.port in ifgrp_ports_detail['ports']:
                        remove_ports_exists = True
            elif self.state == 'present':
                if self.port:
                    if not ifgrp_ports_detail['ports']:
                        add_ports_exists = False
                        changed = True
                    else:
                        if self.port not in ifgrp_ports_detail['ports']:
                            add_ports_exists = False
                            changed = True
        else:
            if self.state == 'present':
                changed = True

        if changed:
            if self.module.check_mode:
                pass
            else:
                if self.state == 'present':
                    if not ifgroup_exists:
                        self.create_if_grp()
                        if self.port:
                            self.add_port_to_if_grp()
                    else:
                        if not add_ports_exists:
                            self.add_port_to_if_grp()
                elif self.state == 'absent':
                    if remove_ports_exists:
                        self.remove_port_to_if_grp()
                    self.delete_if_grp()

        self.module.exit_json(changed=changed)