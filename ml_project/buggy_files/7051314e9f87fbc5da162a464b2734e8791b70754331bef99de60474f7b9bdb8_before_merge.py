def update_distribution(
    name,
    config,
    tags=None,
    region=None,
    key=None,
    keyid=None,
    profile=None,
):
    '''
    Update the config (and optionally tags) for the CloudFront distribution with the given name.

    name
        Name of the CloudFront distribution

    config
        Configuration for the distribution

    tags
        Tags to associate with the distribution

    region
        Region to connect to

    key
        Secret key to use

    keyid
        Access key to use

    profile
        A dict with region, key, and keyid,
        or a pillar key (string) that contains such a dict.

    CLI Example:

    .. code-block:: bash

        salt myminion boto_cloudfront.update_distribution name=mydistribution profile=awsprofile \
            config='{"Comment":"partial configuration","Enabled":true}'
    '''
    distribution_ret = get_distribution(
        name,
        region=region,
        key=key,
        keyid=keyid,
        profile=profile
    )
    if 'error' in distribution_result:
        return distribution_result
    dist_with_tags = distribution_result['result']

    current_distribution = dist_with_tags['distribution']
    current_config = current_distribution['DistributionConfig']
    current_tags = dist_with_tags['tags']
    etag = dist_with_tags['etag']

    config_diff = __utils__['dictdiffer.deep_diff'](current_config, config)
    if tags:
        tags_diff = __utils__['dictdiffer.deep_diff'](current_tags, tags)

    conn = _get_conn(region=region, key=key, keyid=keyid, profile=profile)
    try:
        if 'old' in config_diff or 'new' in config_diff:
            conn.update_distribution(
                DistributionConfig=config,
                Id=current_distribution['Id'],
                IfMatch=etag,
            )
        if tags:
            arn = current_distribution['ARN']
            if 'new' in tags_diff:
                tags_to_add = {
                    'Items': [
                        {'Key': k, 'Value': v}
                        for k, v in six.iteritems(tags_diff['new'])
                    ],
                }
                conn.tag_resource(
                    Resource=arn,
                    Tags=tags_to_add,
                )
            if 'old' in tags_diff:
                tags_to_remove = {
                    'Items': list(tags_diff['old'].keys()),
                }
                conn.untag_resource(
                    Resource=arn,
                    TagKeys=tags_to_remove,
                )
    except botocore.exceptions.ClientError as err:
        return {'error': __utils__['boto3.get_error'](err)}
    finally:
        _cache_id(
            'cloudfront',
            sub_resource=name,
            invalidate=True,
            region=region,
            key=key,
            keyid=keyid,
            profile=profile,
        )

    return {'result': True}