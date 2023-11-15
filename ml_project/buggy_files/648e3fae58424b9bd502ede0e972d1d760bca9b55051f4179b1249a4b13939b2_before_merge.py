    def process(self, resources):
        client = local_session(self.manager.session_factory).client('iam')
        error = None
        if self.data.get('force', False):
            policy_setter = self.manager.action_registry['set-policy'](
                {'state': 'detached', 'arn': '*'}, self.manager)
            policy_setter.process(resources)
        for r in resources:
            try:
                client.delete_role(RoleName=r['RoleName'])
            except client.exceptions.DeleteConflictException as e:
                self.log.warning(
                    "Role:%s cannot be deleted, set force to detach policy and delete"
                    % r['Arn'])
                error = e
            except client.exceptions.NoSuchEntityException:
                continue
            except client.exceptions.UnmodifiableEntityException:
                continue
        if error:
            raise error