    def _get_instance_user_data(self, instance):
        # Query the user data if we need to
        if 'userdata' in instance:
            return instance['userdata']

        user_data = ""
        if self.get_user_data() is not None and instance.get('id'):
            res = self.query_api('getVirtualMachineUserData', virtualmachineid=instance['id'])
            user_data = res['virtualmachineuserdata'].get('userdata', "")
        return user_data