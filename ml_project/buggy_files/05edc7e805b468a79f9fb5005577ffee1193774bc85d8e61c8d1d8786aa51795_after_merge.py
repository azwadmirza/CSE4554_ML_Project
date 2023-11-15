    def _ensure_listeners_default_action_has_arn(self, listeners):
        """
        If a listener DefaultAction has been passed with a Target Group Name instead of ARN, lookup the ARN and
        replace the name.

        :param listeners: a list of listener dicts
        :return: the same list of dicts ensuring that each listener DefaultActions dict has TargetGroupArn key. If a TargetGroupName key exists, it is removed.
        """

        if not listeners:
            listeners = []

        fixed_listeners = []
        for listener in listeners:
            fixed_actions = []
            for action in listener['DefaultActions']:
                if 'TargetGroupName' in action:
                    action['TargetGroupArn'] = convert_tg_name_to_arn(self.connection,
                                                                      self.module,
                                                                      action['TargetGroupName'])
                    del action['TargetGroupName']
                fixed_actions.append(action)
            listener['DefaultActions'] = fixed_actions
            fixed_listeners.append(listener)

        return fixed_listeners