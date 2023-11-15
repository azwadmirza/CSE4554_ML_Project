    def add(self):

        try:
            # Rules is not a valid parameter for create_listener
            if 'Rules' in self.listener:
                self.listener.pop('Rules')
            AWSRetry.jittered_backoff()(self.connection.create_listener)(LoadBalancerArn=self.elb_arn, **self.listener)
        except (BotoCoreError, ClientError) as e:
            if '"Order", must be one of: Type, TargetGroupArn' in str(e):
                self.module.fail_json(msg="installed version of botocore does not support "
                                          "multiple actions, please upgrade botocore to version "
                                          "1.10.30 or higher")
            else:
                self.module.fail_json_aws(e)