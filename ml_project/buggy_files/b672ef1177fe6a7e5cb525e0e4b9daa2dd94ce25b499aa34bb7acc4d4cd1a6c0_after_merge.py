    def apply(self):
        create_delete_decision = {}
        modify = {}
        netapp_utils.ems_log_event("na_ontap_user", self.server)
        for application in self.parameters['applications']:
            current = self.get_user(application)
            cd_action = self.na_helper.get_cd_action(current, self.parameters)
            if cd_action is not None:
                create_delete_decision[application] = cd_action
        if not create_delete_decision and self.parameters.get('state') == 'present':
            if self.parameters.get('set_password') is not None:
                self.na_helper.changed = True
            current = self.get_user()
            if current is not None:
                current['lock_user'] = self.na_helper.get_value_for_bool(True, current['lock_user'])
            modify = self.na_helper.get_modified_attributes(current, self.parameters)

        if self.na_helper.changed:
            if self.module.check_mode:
                pass
            else:
                if create_delete_decision:
                    for cd_action in create_delete_decision:
                        if create_delete_decision[cd_action] == 'create':
                            self.create_user(cd_action)
                        elif create_delete_decision[cd_action] == 'delete':
                            self.delete_user(cd_action)
                elif modify:
                    if self.parameters.get('lock_user'):
                        self.lock_given_user()
                    else:
                        self.unlock_given_user()
                elif not create_delete_decision and self.parameters.get('set_password') is not None:
                    # if change password return false nothing has changed so we need to set changed to False
                    self.na_helper.changed = self.change_password()
        self.module.exit_json(changed=self.na_helper.changed)