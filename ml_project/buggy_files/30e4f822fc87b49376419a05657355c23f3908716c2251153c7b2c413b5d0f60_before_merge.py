    def create(self):
        """
        Create a listener rule

        :return:
        """

        try:
            self.rule['ListenerArn'] = self.listener_arn
            self.rule['Priority'] = int(self.rule['Priority'])
            AWSRetry.jittered_backoff()(self.connection.create_rule)(**self.rule)
        except (BotoCoreError, ClientError) as e:
            self.module.fail_json_aws(e)

        self.changed = True