def get_resource_tag_targets(resource, target_tag_keys):
    if 'Tags' not in resource:
        return []
    tags = {tag['Key']: tag['Value'] for tag in resource['Tags']}
    targets = []
    for target_tag_key in target_tag_keys:
        if target_tag_key in tags:
            targets.append(tags[target_tag_key])
    return targets