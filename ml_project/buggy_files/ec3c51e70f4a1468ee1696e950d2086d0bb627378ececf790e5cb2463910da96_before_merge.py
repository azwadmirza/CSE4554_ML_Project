def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            bucket=dict(required=True),
            dest=dict(default=None, type='path'),
            encrypt=dict(default=True, type='bool'),
            encryption_mode=dict(choices=['AES256', 'aws:kms'], default='AES256'),
            expiry=dict(default=600, type='int', aliases=['expiration']),
            headers=dict(type='dict'),
            marker=dict(default=""),
            max_keys=dict(default=1000, type='int'),
            metadata=dict(type='dict'),
            mode=dict(choices=['get', 'put', 'delete', 'create', 'geturl', 'getstr', 'delobj', 'list'], required=True),
            object=dict(),
            permission=dict(type='list', default=['private']),
            version=dict(default=None),
            overwrite=dict(aliases=['force'], default='always'),
            prefix=dict(default=""),
            retries=dict(aliases=['retry'], type='int', default=0),
            s3_url=dict(aliases=['S3_URL']),
            dualstack=dict(default='no', type='bool'),
            rgw=dict(default='no', type='bool'),
            src=dict(),
            ignore_nonexistent_bucket=dict(default=False, type='bool'),
            encryption_kms_key_id=dict()
        ),
    )
    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[['mode', 'put', ['src', 'object']],
                     ['mode', 'get', ['dest', 'object']],
                     ['mode', 'getstr', ['object']],
                     ['mode', 'geturl', ['object']]],
    )

    bucket = module.params.get('bucket')
    encrypt = module.params.get('encrypt')
    expiry = module.params.get('expiry')
    dest = module.params.get('dest', '')
    headers = module.params.get('headers')
    marker = module.params.get('marker')
    max_keys = module.params.get('max_keys')
    metadata = module.params.get('metadata')
    mode = module.params.get('mode')
    obj = module.params.get('object')
    version = module.params.get('version')
    overwrite = module.params.get('overwrite')
    prefix = module.params.get('prefix')
    retries = module.params.get('retries')
    s3_url = module.params.get('s3_url')
    dualstack = module.params.get('dualstack')
    rgw = module.params.get('rgw')
    src = module.params.get('src')
    ignore_nonexistent_bucket = module.params.get('ignore_nonexistent_bucket')

    object_canned_acl = ["private", "public-read", "public-read-write", "aws-exec-read", "authenticated-read", "bucket-owner-read", "bucket-owner-full-control"]
    bucket_canned_acl = ["private", "public-read", "public-read-write", "authenticated-read"]

    if overwrite not in ['always', 'never', 'different']:
        if module.boolean(overwrite):
            overwrite = 'always'
        else:
            overwrite = 'never'

    region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)

    if region in ('us-east-1', '', None):
        # default to US Standard region
        location = 'us-east-1'
    else:
        # Boto uses symbolic names for locations but region strings will
        # actually work fine for everything except us-east-1 (US Standard)
        location = region

    if module.params.get('object'):
        obj = module.params['object']
        # If there is a top level object, do nothing - if the object starts with /
        # remove the leading character to maintain compatibility with Ansible versions < 2.4
        if obj.startswith('/'):
            obj = obj[1:]

    # Bucket deletion does not require obj.  Prevents ambiguity with delobj.
    if obj and mode == "delete":
        module.fail_json(msg='Parameter obj cannot be used with mode=delete')

    # allow eucarc environment variables to be used if ansible vars aren't set
    if not s3_url and 'S3_URL' in os.environ:
        s3_url = os.environ['S3_URL']

    if dualstack and s3_url is not None and 'amazonaws.com' not in s3_url:
        module.fail_json(msg='dualstack only applies to AWS S3')

    if dualstack and not module.botocore_at_least('1.4.45'):
        module.fail_json(msg='dualstack requires botocore >= 1.4.45')

    # rgw requires an explicit url
    if rgw and not s3_url:
        module.fail_json(msg='rgw flavour requires s3_url')

    # Look at s3_url and tweak connection settings
    # if connecting to RGW, Walrus or fakes3
    if s3_url:
        for key in ['validate_certs', 'security_token', 'profile_name']:
            aws_connect_kwargs.pop(key, None)
    s3 = get_s3_connection(module, aws_connect_kwargs, location, rgw, s3_url)

    validate = not ignore_nonexistent_bucket

    # separate types of ACLs
    bucket_acl = [acl for acl in module.params.get('permission') if acl in bucket_canned_acl]
    object_acl = [acl for acl in module.params.get('permission') if acl in object_canned_acl]
    error_acl = [acl for acl in module.params.get('permission') if acl not in bucket_canned_acl and acl not in object_canned_acl]
    if error_acl:
        module.fail_json(msg='Unknown permission specified: %s' % error_acl)

    # First, we check to see if the bucket exists, we get "bucket" returned.
    bucketrtn = bucket_check(module, s3, bucket, validate=validate)

    if validate and mode not in ('create', 'put', 'delete') and not bucketrtn:
        module.fail_json(msg="Source bucket cannot be found.")

    # If our mode is a GET operation (download), go through the procedure as appropriate ...
    if mode == 'get':
        # Next, we check to see if the key in the bucket exists. If it exists, it also returns key_matches md5sum check.
        keyrtn = key_check(module, s3, bucket, obj, version=version, validate=validate)
        if keyrtn is False:
            if version:
                module.fail_json(msg="Key %s with version id %s does not exist." % (obj, version))
            else:
                module.fail_json(msg="Key %s does not exist." % obj)

        # If the destination path doesn't exist or overwrite is True, no need to do the md5sum ETag check, so just download.
        # Compare the remote MD5 sum of the object with the local dest md5sum, if it already exists.
        if path_check(dest):
            # Determine if the remote and local object are identical
            if keysum_compare(module, dest, s3, bucket, obj, version=version):
                sum_matches = True
                if overwrite == 'always':
                    try:
                        download_s3file(module, s3, bucket, obj, dest, retries, version=version)
                    except Sigv4Required:
                        s3 = get_s3_connection(module, aws_connect_kwargs, location, rgw, s3_url, sig_4=True)
                        download_s3file(module, s3, bucket, obj, dest, retries, version=version)
                else:
                    module.exit_json(msg="Local and remote object are identical, ignoring. Use overwrite=always parameter to force.", changed=False)
            else:
                sum_matches = False

                if overwrite in ('always', 'different'):
                    try:
                        download_s3file(module, s3, bucket, obj, dest, retries, version=version)
                    except Sigv4Required:
                        s3 = get_s3_connection(module, aws_connect_kwargs, location, rgw, s3_url, sig_4=True)
                        download_s3file(module, s3, bucket, obj, dest, retries, version=version)
                else:
                    module.exit_json(msg="WARNING: Checksums do not match. Use overwrite parameter to force download.")
        else:
            try:
                download_s3file(module, s3, bucket, obj, dest, retries, version=version)
            except Sigv4Required:
                s3 = get_s3_connection(module, aws_connect_kwargs, location, rgw, s3_url, sig_4=True)
                download_s3file(module, s3, bucket, obj, dest, retries, version=version)

    # if our mode is a PUT operation (upload), go through the procedure as appropriate ...
    if mode == 'put':

        # if putting an object in a bucket yet to be created, acls for the bucket and/or the object may be specified
        # these were separated into the variables bucket_acl and object_acl above

        # Lets check the src path.
        if not path_check(src):
            module.fail_json(msg="Local object for PUT does not exist")

        # Lets check to see if bucket exists to get ground truth.
        if bucketrtn:
            keyrtn = key_check(module, s3, bucket, obj, version=version, validate=validate)

        # Lets check key state. Does it exist and if it does, compute the ETag md5sum.
        if bucketrtn and keyrtn:
            # Compare the local and remote object
            if keysum_compare(module, src, s3, bucket, obj):
                sum_matches = True
                if overwrite == 'always':
                    # only use valid object acls for the upload_s3file function
                    module.params['permission'] = object_acl
                    upload_s3file(module, s3, bucket, obj, src, expiry, metadata, encrypt, headers)
                else:
                    get_download_url(module, s3, bucket, obj, expiry, changed=False)
            else:
                sum_matches = False
                if overwrite in ('always', 'different'):
                    # only use valid object acls for the upload_s3file function
                    module.params['permission'] = object_acl
                    upload_s3file(module, s3, bucket, obj, src, expiry, metadata, encrypt, headers)
                else:
                    module.exit_json(msg="WARNING: Checksums do not match. Use overwrite parameter to force upload.")

        # If neither exist (based on bucket existence), we can create both.
        if not bucketrtn:
            # only use valid bucket acls for create_bucket function
            module.params['permission'] = bucket_acl
            create_bucket(module, s3, bucket, location)
            # only use valid object acls for the upload_s3file function
            module.params['permission'] = object_acl
            upload_s3file(module, s3, bucket, obj, src, expiry, metadata, encrypt, headers)

        # If bucket exists but key doesn't, just upload.
        if bucketrtn and not keyrtn:
            # only use valid object acls for the upload_s3file function
            module.params['permission'] = object_acl
            upload_s3file(module, s3, bucket, obj, src, expiry, metadata, encrypt, headers)

    # Delete an object from a bucket, not the entire bucket
    if mode == 'delobj':
        if obj is None:
            module.fail_json(msg="object parameter is required")
        if bucket:
            deletertn = delete_key(module, s3, bucket, obj)
            if deletertn is True:
                module.exit_json(msg="Object deleted from bucket %s." % bucket, changed=True)
        else:
            module.fail_json(msg="Bucket parameter is required.")

    # Delete an entire bucket, including all objects in the bucket
    if mode == 'delete':
        if bucket:
            deletertn = delete_bucket(module, s3, bucket)
            if deletertn is True:
                module.exit_json(msg="Bucket %s and all keys have been deleted." % bucket, changed=True)
        else:
            module.fail_json(msg="Bucket parameter is required.")

    # Support for listing a set of keys
    if mode == 'list':
        exists = bucket_check(module, s3, bucket)

        # If the bucket does not exist then bail out
        if not exists:
            module.fail_json(msg="Target bucket (%s) cannot be found" % bucket)

        list_keys(module, s3, bucket, prefix, marker, max_keys)

    # Need to research how to create directories without "populating" a key, so this should just do bucket creation for now.
    # WE SHOULD ENABLE SOME WAY OF CREATING AN EMPTY KEY TO CREATE "DIRECTORY" STRUCTURE, AWS CONSOLE DOES THIS.
    if mode == 'create':

        # if both creating a bucket and putting an object in it, acls for the bucket and/or the object may be specified
        # these were separated above into the variables bucket_acl and object_acl

        if bucket and not obj:
            if bucketrtn:
                module.exit_json(msg="Bucket already exists.", changed=False)
            else:
                # only use valid bucket acls when creating the bucket
                module.params['permission'] = bucket_acl
                module.exit_json(msg="Bucket created successfully", changed=create_bucket(module, s3, bucket, location))
        if bucket and obj:
            if obj.endswith('/'):
                dirobj = obj
            else:
                dirobj = obj + "/"
            if bucketrtn:
                if key_check(module, s3, bucket, dirobj):
                    module.exit_json(msg="Bucket %s and key %s already exists." % (bucket, obj), changed=False)
                else:
                    # setting valid object acls for the create_dirkey function
                    module.params['permission'] = object_acl
                    create_dirkey(module, s3, bucket, dirobj, encrypt)
            else:
                # only use valid bucket acls for the create_bucket function
                module.params['permission'] = bucket_acl
                created = create_bucket(module, s3, bucket, location)
                # only use valid object acls for the create_dirkey function
                module.params['permission'] = object_acl
                create_dirkey(module, s3, bucket, dirobj, encrypt)

    # Support for grabbing the time-expired URL for an object in S3/Walrus.
    if mode == 'geturl':
        if not bucket and not obj:
            module.fail_json(msg="Bucket and Object parameters must be set")

        keyrtn = key_check(module, s3, bucket, obj, version=version, validate=validate)
        if keyrtn:
            get_download_url(module, s3, bucket, obj, expiry)
        else:
            module.fail_json(msg="Key %s does not exist." % obj)

    if mode == 'getstr':
        if bucket and obj:
            keyrtn = key_check(module, s3, bucket, obj, version=version, validate=validate)
            if keyrtn:
                try:
                    download_s3str(module, s3, bucket, obj, version=version)
                except Sigv4Required:
                    s3 = get_s3_connection(module, aws_connect_kwargs, location, rgw, s3_url, sig_4=True)
                    download_s3str(module, s3, bucket, obj, version=version)
            elif version is not None:
                module.fail_json(msg="Key %s with version id %s does not exist." % (obj, version))
            else:
                module.fail_json(msg="Key %s does not exist." % obj)

    module.exit_json(failed=False)