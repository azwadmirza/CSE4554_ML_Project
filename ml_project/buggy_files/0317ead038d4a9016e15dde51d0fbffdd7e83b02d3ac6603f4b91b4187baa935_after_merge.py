def convert_to_group_ids(groups, vpc_id=None, vpc_name=None, region=None, key=None,
                         keyid=None, profile=None):
    '''
    Given a list of security groups and a vpc_id, convert_to_group_ids will
    convert all list items in the given list to security group ids.

    CLI example::

        salt myminion boto_secgroup.convert_to_group_ids mysecgroup vpc-89yhh7h
    '''
    log.debug('security group contents %s pre-conversion', groups)
    group_ids = []
    for group in groups:
        group_id = get_group_id(name=group, vpc_id=vpc_id,
                                vpc_name=vpc_name, region=region,
                                key=key, keyid=keyid, profile=profile)
        if not group_id:
            # Security groups are a big deal - need to fail if any can't be resolved...
            # But... if we're running in test mode, it may just be that the SG is scheduled
            # to be created, and thus WOULD have been there if running "for real"...
            if __opts__['test']:
                log.warn('Security Group `%s` could not be resolved to an ID.  This may '
                         'cause a failure when not running in test mode.', group)
                return []
            else:
                raise CommandExecutionError('Could not resolve Security Group name '
                                            '{0} to a Group ID'.format(group))
        else:
            group_ids.append(six.text_type(group_id))
    log.debug('security group contents %s post-conversion', group_ids)
    return group_ids