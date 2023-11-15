    def apply(self):
        self.autosupport_log()
        current = self.get_if_grp()
        cd_action = self.na_helper.get_cd_action(current, self.parameters)
        if current and self.parameters['state'] == 'present':
            current_ports = self.get_if_grp_ports()
            modify = self.na_helper.get_modified_attributes(current_ports, self.parameters)
        if self.na_helper.changed:
            if self.module.check_mode:
                pass
            else:
                if cd_action == 'create':
                    self.create_if_grp()
                elif cd_action == 'delete':
                    self.delete_if_grp()
                elif modify:
                    self.modify_ports(current_ports['ports'])
        self.module.exit_json(changed=self.na_helper.changed)