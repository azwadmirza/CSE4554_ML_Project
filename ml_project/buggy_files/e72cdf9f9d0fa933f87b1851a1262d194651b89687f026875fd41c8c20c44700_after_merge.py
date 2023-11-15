def create_dirkey(module, s3, bucket, obj):
    if module.check_mode:
        module.exit_json(msg="PUT operation skipped - running in check mode", changed=True)
    try:
        s3.put_object(Bucket=bucket, Key=obj, Body=b'')
        for acl in module.params.get('permission'):
            s3.put_object_acl(ACL=acl, Bucket=bucket, Key=obj)
        module.exit_json(msg="Virtual directory %s created in bucket %s" % (obj, bucket), changed=True)
    except botocore.exceptions.ClientError as e:
        module.fail_json(msg="Failed while creating object %s." % obj, exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))