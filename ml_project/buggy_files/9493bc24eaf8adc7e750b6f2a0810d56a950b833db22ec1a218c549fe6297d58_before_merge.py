    def modify(self):

        try:
            # Rules is not a valid parameter for modify_listener
            if 'Rules' in self.listener:
                self.listener.pop('Rules')
            AWSRetry.jittered_backoff()(self.connection.modify_listener)(**self.listener)
        except (BotoCoreError, ClientError) as e:
            self.module.fail_json_aws(e)