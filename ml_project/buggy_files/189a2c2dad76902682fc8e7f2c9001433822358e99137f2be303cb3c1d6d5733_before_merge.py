    def add(self):

        try:
            # Rules is not a valid parameter for create_listener
            if 'Rules' in self.listener:
                self.listener.pop('Rules')
            AWSRetry.jittered_backoff()(self.connection.create_listener)(LoadBalancerArn=self.elb_arn, **self.listener)
        except (BotoCoreError, ClientError) as e:
            self.module.fail_json_aws(e)