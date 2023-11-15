def json_query(data, expr):
    '''Query data using jmespath query language ( http://jmespath.org ). Example:
    - debug: msg="{{ instance | json_query(tagged_instances[*].block_device_mapping.*.volume_id') }}"
    '''
    if not HAS_LIB:
        raise AnsibleError('You need to install "jmespath" prior to running '
                           'json_query filter')

    try:
        return jmespath.search(expr, data)
    except jmespath.exceptions.JMESPathError as e:
        raise AnsibleFilterError('JMESPathError in json_query filter plugin:\n%s' % e)
    except Exception as e:
        # For older jmespath, we can get ValueError and TypeError without much info.
        raise AnsibleFilterError('Error in jmespath.search in json_query filter plugin:\n%s' % e)