    def modify(self):
        """
        Modify a listener rule

        :return:
        """

        try:
            del self.rule['Priority']
            AWSRetry.jittered_backoff()(self.connection.modify_rule)(**self.rule)
        except (BotoCoreError, ClientError) as e:
            self.module.fail_json_aws(e)

        self.changed = True