    def modify(self):
        """
        Modify a listener rule

        :return:
        """

        try:
            del self.rule['Priority']
            AWSRetry.jittered_backoff()(self.connection.modify_rule)(**self.rule)
        except (BotoCoreError, ClientError) as e:
            if '"Order", must be one of: Type, TargetGroupArn' in str(e):
                self.module.fail_json(msg="installed version of botocore does not support "
                                          "multiple actions, please upgrade botocore to version "
                                          "1.10.30 or higher")
            else:
                self.module.fail_json_aws(e)

        self.changed = True