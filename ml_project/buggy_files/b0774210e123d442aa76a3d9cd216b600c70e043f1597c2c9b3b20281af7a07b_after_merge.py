def ensure_tags(conn, module, subnet, tags, purge_tags, start_time):
    changed = False

    filters = ansible_dict_to_boto3_filter_list({'resource-id': subnet['id'], 'resource-type': 'subnet'})
    try:
        cur_tags = conn.describe_tags(Filters=filters)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't describe tags")

    to_update, to_delete = compare_aws_tags(boto3_tag_list_to_ansible_dict(cur_tags.get('Tags')), tags, purge_tags)

    if to_update:
        try:
            if not module.check_mode:
                AWSRetry.exponential_backoff(
                    catch_extra_error_codes=['InvalidSubnetID.NotFound']
                )(conn.create_tags)(
                    Resources=[subnet['id']],
                    Tags=ansible_dict_to_boto3_tag_list(to_update)
                )

            changed = True
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't create tags")

    if to_delete:
        try:
            if not module.check_mode:
                tags_list = []
                for key in to_delete:
                    tags_list.append({'Key': key})

                AWSRetry.exponential_backoff(
                    catch_extra_error_codes=['InvalidSubnetID.NotFound']
                )(conn.delete_tags)(Resources=[subnet['id']], Tags=tags_list)

            changed = True
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't delete tags")

    if module.params['wait'] and not module.check_mode:
        # Wait for tags to be updated
        filters = [{'Name': 'tag:{0}'.format(k), 'Values': [v]} for k, v in tags.items()]
        handle_waiter(conn, module, 'subnet_exists',
                      {'SubnetIds': [subnet['id']], 'Filters': filters}, start_time)

    return changed