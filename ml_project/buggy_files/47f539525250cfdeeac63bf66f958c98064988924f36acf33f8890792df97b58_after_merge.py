    def process(self, resources, event):
        if event is None:
            return

        user_info = self.get_tag_value(event)

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

        new_tags = {}
        if user_info['user']:
            new_tags[self.data['tag']] = user_info['user']

        # if principal_id_key is set (and value), we'll set the principalId tag.
        principal_id_key = self.data.get('principal_id_tag', None)
        if principal_id_key and user_info['id']:
            new_tags[principal_id_key] = user_info['id']

        if new_tags:
            self.set_resource_tags(new_tags, untagged_resources)
        return new_tags