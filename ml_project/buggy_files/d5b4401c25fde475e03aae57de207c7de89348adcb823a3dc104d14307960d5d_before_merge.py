    def process_resource(self, client, r, related_tags, tag_keys, tag_action):
        tags = {}
        resource_tags = {
            t['Key']: t['Value'] for t in r.get('Tags', []) if not t['Key'].startswith('aws:')}

        if tag_keys == '*':
            tags = {k: v for k, v in related_tags.items()
                    if resource_tags.get(k) != v}
        else:
            tags = {k: v for k, v in related_tags.items()
                    if k in tag_keys and resource_tags.get(k) != v}
        if not tags:
            return
        if not isinstance(tag_action, UniversalTag):
            tags = [{'Key': k, 'Value': v} for k, v in tags.items()]
        tag_action.process_resource_set(
            client,
            resource_set=[r],
            tags=tags)
        return True