def ensure_tags(conn, module, subnet, tags, add_only, check_mode):
    cur_tags = subnet['tags']

    to_delete = dict((k, cur_tags[k]) for k in cur_tags if k not in tags)
    if to_delete and not add_only and not check_mode:
        try:
            conn.delete_tags(Resources=[subnet['id']], Tags=ansible_dict_to_boto3_tag_list(to_delete))
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't delete tags")

    to_add = dict((k, tags[k]) for k in tags if k not in cur_tags or cur_tags[k] != tags[k])
    if to_add and not check_mode:
        try:
            conn.create_tags(Resources=[subnet['id']], Tags=ansible_dict_to_boto3_tag_list(to_add))
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't create tags")