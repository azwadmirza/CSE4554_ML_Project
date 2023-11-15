def filter_list(s3, bucket, s3filelist, strategy):
    keeplist = list(s3filelist)

    for e in keeplist:
        e['_strategy'] = strategy

    # init/fetch info from S3 if we're going to use it for comparisons
    if not strategy == 'force':
        keeplist = head_s3(s3, bucket, s3filelist)

    # now actually run the strategies
    if strategy == 'checksum':
        for entry in keeplist:
            if entry.get('s3_head'):
                # since we have a remote s3 object, compare the values.
                if entry['s3_head']['ETag'] == entry['local_etag']:
                    # files match, so remove the entry
                    entry['skip_flag'] = True
                else:
                    # file etags don't match, keep the entry.
                    pass
            else:  # we don't have an etag, so we'll keep it.
                pass
    elif strategy == 'date_size':
        for entry in keeplist:
            if entry.get('s3_head'):
                # fstat = entry['stat']
                local_modified_epoch = entry['modified_epoch']
                local_size = entry['bytes']

                # py2's datetime doesn't have a timestamp() field, so we have to revert to something more awkward.
                # remote_modified_epoch = entry['s3_head']['LastModified'].timestamp()
                remote_modified_datetime = entry['s3_head']['LastModified']
                delta = (remote_modified_datetime - datetime.datetime(1970, 1, 1, tzinfo=tz.tzutc()))
                remote_modified_epoch = delta.seconds + (delta.days * 86400)

                remote_size = entry['s3_head']['ContentLength']

                entry['whytime'] = '{0} / {1}'.format(local_modified_epoch, remote_modified_epoch)
                entry['whysize'] = '{0} / {1}'.format(local_size, remote_size)

                if local_modified_epoch <= remote_modified_epoch or local_size == remote_size:
                    entry['skip_flag'] = True
            else:
                entry['why'] = "no s3_head"
    # else: probably 'force'. Basically we don't skip with any with other strategies.
    else:
        pass

    # prune 'please skip' entries, if any.
    return [x for x in keeplist if not x.get('skip_flag')]