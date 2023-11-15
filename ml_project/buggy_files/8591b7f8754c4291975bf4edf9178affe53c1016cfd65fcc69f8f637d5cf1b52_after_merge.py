    def change_password(self):
        """
        Changes the password

        :return:
            True if password updated
            False if password is not updated
        :rtype: bool
        """
        # self.server.set_vserver(self.parameters['vserver'])
        modify_password = netapp_utils.zapi.NaElement.create_node_with_children(
            'security-login-modify-password', **{
                'new-password': str(self.parameters.get('set_password')),
                'user-name': self.parameters['name']})
        try:
            self.server.invoke_successfully(modify_password,
                                            enable_tunneling=True)
        except netapp_utils.zapi.NaApiError as error:
            if to_native(error.code) == '13114':
                return False
            # if the user give the same password, instead of returning an error, return ok
            if to_native(error.code) == '13214' and error.message.startswith('New password must be different than the old password.'):
                return False
            self.module.fail_json(msg='Error setting password for user %s: %s' % (self.parameters['name'], to_native(error)),
                                      exception=traceback.format_exc())

        self.server.set_vserver(None)
        return True