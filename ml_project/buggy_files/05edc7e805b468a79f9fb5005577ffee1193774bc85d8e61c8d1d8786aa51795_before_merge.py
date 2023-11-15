    def _ensure_listeners_default_action_has_arn(self, listeners):
        """
        If a listener DefaultAction has been passed with a Target Group Name instead of ARN, lookup the ARN and
        replace the name.

        :param listeners: a list of listener dicts
        :return: the same list of dicts ensuring that each listener DefaultActions dict has TargetGroupArn key. If a TargetGroupName key exists, it is removed.
        """

        if not listeners:
            listeners = []

        for listener in listeners:
            if 'TargetGroupName' in listener['DefaultActions'][0]:
                listener['DefaultActions'][0]['TargetGroupArn'] = convert_tg_name_to_arn(self.connection, self.module,
                                                                                         listener['DefaultActions'][0]['TargetGroupName'])
                del listener['DefaultActions'][0]['TargetGroupName']

        return listeners