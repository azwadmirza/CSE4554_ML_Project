def _mask_object(object_to_be_masked, topfile):
    '''
    Given an object with potential secrets (or other data that should not be
    returned), mask the contents of that object as configured in the mask
    configuration file. The mask configuration file used is defined by the
    top data in the ``topfile`` argument.

    If multiple mask.yaml files are matched in the topfile, the data within
    them will be recursively merged.

    If no matching mask_files are found in the top.mask file, no masking will
    happen.

    Note that this function has side effects: alterations to
    ``object_to_be_masked`` will be made in place.

    Sample mask.yaml data (with inline documentation):

    .. code-block:: yaml

        # Pattern that will replace whatever is masked
        mask_with: '***masked*by*hubble***'

        # Target and mask strings based on regex patterns
        # Can limit search specific queries and columns
        blacklisted_strings:
            - query_name: 'running_procs'  # Name of the osquery to be masked.
                                           # Put '*' to match all queries. Note
                                           # that query_name doesn't support
                                           # full globbing. '*' is just given
                                           # special treatment.
              column: 'command_line'  # Column name in the osquery to be masked. No regex or glob support
              # See below for documentation of these blacklisted patterns
              blacklisted_patterns:
                  - '(prefix)(password)(suffix)'


        # Some osquery results are formed as lists of dicts. We can mask
        # based on variable names within these dicts.
        blacklisted_objects:

            - query_name: 'running_procs'  # Name of the osquery to be masked.
                                           # Put '*' to match all queries. Note
                                           # that query_name doesn't support
                                           # full globbing. '*' is just given
                                           # special treatment.
              column: 'environment'  # Column name in the osquery to be masked. No regex or glob support
              attribute_to_check: 'variable_name' # In the inner dict, this is the key
                                                  # to check for blacklisted_patterns
              attributes_to_mask: # Values under these keys in the dict will be
                - 'value'  # masked, assuming one of the blacklisted_patterns
                           # is found under attribute_to_check in the same dict
              blacklisted_patterns:  # Strings to look for under attribute_to_check. Globbing support
                - 'ETCDCTL_READ_PASSWORD'
                - 'ETCDCTL_WRITE_PASSWORD'
                - '*PASSWORD*'

    blacklisted_patterns (for blacklisted_strings)

        Blacklisted patterns are regular expressions, and have a prefix, a
        secret, and a suffix. Nebula uses regex groups to maintain the prefix
        and suffix, *which are not masked*. Only the password is masked.

        If you don't need a suffix or a prefix, leave those sets of parenthesis
        blank. Do not remove any parenthesis, or else your password could
        remain unmasked!

        blacklisted_patterns is formed as a list. These patterns are processed
        (and substituted) in order.

    blacklisted_patterns (for blacklisted_objects)

        For objects, the pattern applies to the variable name, and doesn't
        support regex. For example, you might have data formed like this::

            [{ value: 'SOME_PASSWORD', variable_name: 'ETCDCTL_READ_PASSWORD' }]

        The attribute_to_check would be ``variable_name`` and the pattern would
        be ``ETCDCTL_READ_PASSWORD``. The attribute_to_mask would be ``value``.
        All dicts with ``variable_name`` in the list of blacklisted_patterns
        would have the value under their ``value`` key masked.
    '''
    try:
        mask = {}
        if topfile is None:
            topfile = 'salt://hubblestack_nebula_v2/top.mask'
        mask_files = _get_top_data(topfile)
        mask_files = ['salt://hubblestack_nebula_v2/' + mask_file.replace('.', '/') + '.yaml'
                      for mask_file in mask_files]
        if not mask_files:
            mask_files = []
        for fh in mask_files:
            if 'salt://' in fh:
                orig_fh = fh
                fh = __salt__['cp.cache_file'](fh)
            if fh is None:
                log.error('Could not find file {0}.'.format(orig_fh))
                return None
            if os.path.isfile(fh):
                with open(fh, 'r') as f:
                    f_data = yaml.safe_load(f)
                    if not isinstance(f_data, dict):
                        raise CommandExecutionError('File data is not formed as a dict {0}'
                                                    .format(f_data))
                    mask = _dict_update(mask, f_data, recursive_update=True, merge_lists=True)

        log.debug('Masking data: {}'.format(mask))

        # Backwards compatibility with mask_by
        mask_with = mask.get('mask_with', mask.get('mask_by', '******'))

        # We can blacklist strings based on their pattern
        for blacklisted_string in mask.get('blacklisted_strings', []):
            query_name = blacklisted_string['query_name']
            column = blacklisted_string['column']
            if query_name != '*':
                for r in object_to_be_masked:
                    for query_result in r.get(query_name, {'data':[]})['data']:
                        if column not in query_result or not isinstance(query_result[column], basestring):
                            # if the column in not present in one data-object, it will
                            # not be present in others as well. Break in that case.
                            # This will happen only if mask.yaml is malformed
                            log.error('masking data references a missing column {0} in query {1}'
                                      .format(column, query_name))
                            break
                        value = query_result[column]
                        for pattern in blacklisted_string['blacklisted_patterns']:
                            value = re.sub(pattern + '()', r'\1' + mask_with + r'\3', value)
                        query_result[column] = value
            else:
                for r in object_to_be_masked:
                    for query_name, query_ret in r.iteritems():
                        for query_result in query_ret['data']:
                            if column not in query_result or not isinstance(query_result[column], basestring):
                                # No error here, since we didn't reference a specific query
                                break
                            value = query_result[column]
                            for pattern in blacklisted_string['blacklisted_patterns']:
                                value = re.sub(pattern + '()', r'\1' + mask_with + r'\3', value)
                            query_result[column] = value


        for blacklisted_object in mask.get('blacklisted_objects', []):
            query_name = blacklisted_object['query_name']
            column = blacklisted_object['column']
            if query_name != '*':
                for r in object_to_be_masked:
                    for query_result in r.get(query_name, {'data':[]})['data']:
                        if column not in query_result or \
                                (isinstance(query_result[column], basestring) and
                                 query_result[column].strip() != ''):
                            # if the column in not present in one data-object, it will
                            # not be present in others as well. Break in that case.
                            # This will happen only if mask.yaml is malformed
                            log.error('masking data references a missing column {0} in query {1}'
                                      .format(column, query_name))
                            break
                        _recursively_mask_objects(query_result[column], blacklisted_object, mask_with)
            else:
                for r in object_to_be_masked:
                    for query_name, query_ret in r.iteritems():
                        for query_result in query_ret['data']:
                            if column not in query_result or \
                                    (isinstance(query_result[column], basestring) and
                                     query_result[column].strip() != '' ):
                                # No error here, since we didn't reference a specific query
                                break
                            _recursively_mask_objects(query_result[column], blacklisted_object, mask_with)
    except Exception as e:
        log.exception('An error occured while masking the passwords: {}'.format(e))

    # Object masked in place, so we don't need to return the object
    return True