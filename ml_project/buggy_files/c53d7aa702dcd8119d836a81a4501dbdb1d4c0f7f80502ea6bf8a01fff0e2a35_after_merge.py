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

        # Some osquery results are formed as lists of dicts. We can mask
        # based on variable names within these dicts.
        blacklisted_objects:

            - query_names:
              - 'running_procs'
              - 'listening_procs'          # List of name(s) of the osquery to be masked.
                                           # Put '*' to match all queries. Note
                                           # that query_names doesn't support
                                           # full globbing. '*' is just given
                                           # special treatment.
              column: 'environment'  # Column name in the osquery to be masked. No regex or glob support
              custom_mask_column: 'environment'  # Column name which stores environment variables
              custom_mask_key: '__hubble_mask__' # Env variable to look for constructing custom blacklist of patterns.
              attribute_to_check: 'variable_name' # Optional attribute
                                                  # In the inner dict, this is the key
                                                  # to check for blacklisted_patterns
                                                  # Will skipped if column specified is of type 'String'
              attributes_to_mask: # Optional attribute, Values under these keys in the dict will be
                - 'value'  # masked, assuming one of the blacklisted_patterns
                           # is found under attribute_to_check in the same dict
                           # Will be skipped if column specified is of type 'String'
              blacklisted_patterns:  # Strings to look for under attribute_to_check. Conditional Globbing support.
                - 'ETCDCTL_READ_PASSWORD'
                - 'ETCDCTL_WRITE_PASSWORD'
                - '*PASSWORD*'  # Enable globbing by setting 'enable_globbing_in_nebula_masking' to True, default False

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
            # We will maintain backward compatibility by keeping two versions of top files and mask files for now
            # Once all hubble servers are updated, we can remove old version of top file and mask file
            # Similar to what we have for nebula and nebula_v2 for older versions and newer versions of profiles
            topfile = 'salt://hubblestack_nebula_v2/top_v2.mask'
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

        log.info("Total number of results to check for masking: {0}".format(len(object_to_be_masked)))
        globbing_enabled = __opts__.get('enable_globbing_in_nebula_masking')

        for blacklisted_object in mask.get('blacklisted_objects', []):
            query_names = blacklisted_object['query_names']
            column = blacklisted_object['column'] # Can be converted to list as well in future if need be
            custom_mask_column = blacklisted_object.get('custom_mask_column', '') # Name of column that stores environment variables
            if '*' in query_names:
                # This means wildcard is specified and each event should be masked, if applicable
                for r in object_to_be_masked:
                    if 'action' in r:
                        # This means data is generated by osquery daemon
                        _mask_event_data(r, None, column, blacklisted_object, mask_with, globbing_enabled)
                    else:
                        # This means data is generated by osquery interactive shell
                        for query_name, query_ret in r.iteritems():
                            for query_result in query_ret['data']:
                                if custom_mask_column and custom_mask_column in query_result:
                                    log.debug("Checking if custom mask patterns are set in environment")
                                    mask_column = query_result[custom_mask_column]
                                    if mask_column and isinstance(mask_column, list):
                                        for column_field in mask_column:
                                            try:
                                                if 'variable_name' in column_field and 'value' in column_field and \
                                                    column_field['variable_name'] == blacklisted_object['custom_mask_key']:
                                                    log.debug("Constructing custom blacklisted patterns based on \
                                                              environment variable '{0}'".format(blacklisted_object['custom_mask_key']))
                                                    blacklisted_object['custom_blacklist'] = [ p.strip() for p in column_field['value'].split(',')
                                                                                                 if p.strip() != blacklisted_object['custom_mask_key']]
                                                else:
                                                    log.debug("Custom mask variable not set in environment. \
                                                              Custom mask key used: {0}".format(blacklisted_object['custom_mask_key']))
                                            except Exception as e:
                                                log.error("Failed to generate custom blacklisted patterns based on hubble mask key")
                                                log.error("Got error: {0}".format(e))
                                if column not in query_result or \
                                        (isinstance(query_result[column], basestring) and
                                        query_result[column].strip() != ''):
                                        # No error here, since we didn't reference a specific query
                                    break
                                if isinstance(query_result[column], basestring):
                                    # If column is of 'string' type, then replace pattern in-place
                                    # No need for recursion here
                                    value = query_result[column]
                                    for pattern in blacklisted_object['blacklisted_patterns']:
                                        value = re.sub(pattern + '()', r'\1' + mask_with + r'\3', value)
                                    query_result[column] = value
                                else:
                                    _perform_masking(query_result[column], blacklisted_object, mask_with, globbing_enabled)
            else:
                # Perform masking on results of specific queries specified in 'query_names'
                for query_name in query_names:
                    for r in object_to_be_masked:
                        if 'action' in r:
                            # This means data is generated by osquery daemon
                            _mask_event_data(r, query_name, column, blacklisted_object, mask_with, globbing_enabled)
                        else:
                            # This means data is generated by osquery interactive shell
                            for query_result in r.get(query_name, {'data':[]})['data']:
                                if custom_mask_column and custom_mask_column in query_result:
                                    log.debug("Checking if custom mask patterns are set in environment")
                                    mask_column = query_result[custom_mask_column]
                                    if mask_column and isinstance(mask_column, list):
                                        for column_field in mask_column:
                                            try:
                                                if 'variable_name' in column_field and 'value' in column_field and \
                                                    column_field['variable_name'] == blacklisted_object['custom_mask_key']:
                                                    log.debug("Constructing custom blacklisted patterns based on \
                                                              environment variable '{0}'".format(blacklisted_object['custom_mask_key']))
                                                    blacklisted_object['custom_blacklist'] = [ p.strip() for p in column_field['value'].split(',')
                                                                                                 if p.strip() != blacklisted_object['custom_mask_key']]
                                                else:
                                                    log.debug("Custom mask variable not set in environment. \
                                                              Custom mask key used: {0}".format(blacklisted_object['custom_mask_key']))
                                            except Exception as e:
                                                log.error("Failed to generate custom blacklisted patterns based on hubble mask key")
                                                log.error("Got error: {0}".format(e))
                                if column not in query_result or \
                                        (isinstance(query_result[column], basestring) and
                                         query_result[column].strip() != ''):
                                        # if the column in not present in one data-object, it will
                                        # not be present in others as well. Break in that case.
                                        # This will happen only if mask.yaml is malformed
                                    log.error('masking data references a missing column {0} in query {1}'
                                              .format(column, query_name))
                                    break
                                if isinstance(query_result[column], basestring):
                                    # If column is of 'string' type, then replace pattern in-place
                                    # No need for recursion here
                                    value = query_result[column]
                                    for pattern in blacklisted_object['blacklisted_patterns']:
                                        value = re.sub(pattern + '()', r'\1' + mask_with + r'\3', value)
                                    query_result[column] = value
                                else:
                                    _perform_masking(query_result[column], blacklisted_object, mask_with, globbing_enabled)
    except Exception as e:
        log.exception('An error occured while masking the passwords: {}'.format(e))

    # Object masked in place, so we don't need to return the object
    return True