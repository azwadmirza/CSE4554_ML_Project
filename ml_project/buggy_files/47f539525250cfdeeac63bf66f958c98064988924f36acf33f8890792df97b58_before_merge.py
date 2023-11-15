    def process(self, resources, event):
        if event is None:
            return
        event = event['detail']
        utype = event['userIdentity']['type']
        if utype not in self.data.get('user-type', ['AssumedRole', 'IAMUser', 'FederatedUser']):
            return

        user = None
        if utype == "IAMUser":
            user = event['userIdentity']['userName']
            principal_id_value = event['userIdentity'].get('principalId', '')
        elif utype == "AssumedRole" or utype == "FederatedUser":
            user = event['userIdentity']['arn']
            prefix, user = user.rsplit('/', 1)
            principal_id_value = event['userIdentity'].get('principalId', '').split(':')[0]
            # instance role
            if user.startswith('i-'):
                return
            # lambda function (old style)
            elif user.startswith('awslambda'):
                return
        if user is None:
            return
        # if the auto-tag-user policy set update to False (or it's unset) then we
        # will skip writing their UserName tag and not overwrite pre-existing values
        if not self.data.get('update', False):
            untagged_resources = []
            # iterating over all the resources the user spun up in this event
            for resource in resources:
                tag_already_set = False
                for tag in resource.get('Tags', ()):
                    if tag['Key'] == self.data['tag']:
                        tag_already_set = True
                        break
                if not tag_already_set:
                    untagged_resources.append(resource)
        # if update is set to True, we will overwrite the userName tag even if
        # the user already set a value
        else:
            untagged_resources = resources

        tag_action = self.manager.action_registry.get('tag')
        new_tags = {
            self.data['tag']: user
        }
        # if principal_id_key is set (and value), we'll set the principalId tag.
        principal_id_key = self.data.get('principal_id_tag', None)
        if principal_id_key and principal_id_value:
            new_tags[principal_id_key] = principal_id_value
        for key, value in new_tags.items():
            tag_action({'key': key, 'value': value}, self.manager).process(untagged_resources)
        return new_tags