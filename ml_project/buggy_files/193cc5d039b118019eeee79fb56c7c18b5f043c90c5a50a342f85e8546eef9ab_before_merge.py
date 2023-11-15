def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='path', required=True, aliases=['filename']),
            dialect=dict(type='str', default='excel'),
            key=dict(type='str'),
            fieldnames=dict(type='list'),
            unique=dict(type='bool', default=True),
            delimiter=dict(type='str'),
            skipinitialspace=dict(type='bool'),
            strict=dict(type='bool'),
        ),
        supports_check_mode=True,
    )

    path = module.params['path']
    dialect = module.params['dialect']
    key = module.params['key']
    fieldnames = module.params['fieldnames']
    unique = module.params['unique']

    if dialect not in csv.list_dialects():
        module.fail_json(msg="Dialect '%s' is not supported by your version of python." % dialect)

    dialect_options = dict(
        delimiter=module.params['delimiter'],
        skipinitialspace=module.params['skipinitialspace'],
        strict=module.params['strict'],
    )

    # Create a dictionary from only set options
    dialect_params = dict((k, v) for k, v in dialect_options.items() if v is not None)
    if dialect_params:
        try:
            csv.register_dialect('custom', dialect, **dialect_params)
        except TypeError as e:
            module.fail_json(msg="Unable to create custom dialect: %s" % to_text(e))
        dialect = 'custom'

    try:
        f = open(path, 'r')
    except (IOError, OSError) as e:
        module.fail_json(msg="Unable to open file: %s" % to_text(e))

    reader = csv.DictReader(f, fieldnames=fieldnames, dialect=dialect)

    if key and key not in reader.fieldnames:
        module.fail_json(msg="Key '%s' was not found in the CSV header fields: %s" % (key, ', '.join(reader.fieldnames)))

    data_dict = dict()
    data_list = list()

    if key is None:
        try:
            for row in reader:
                data_list.append(row)
        except csv.Error as e:
            module.fail_json(msg="Unable to process file: %s" % to_text(e))
    else:
        try:
            for row in reader:
                if unique and row[key] in data_dict:
                    module.fail_json(msg="Key '%s' is not unique for value '%s'" % (key, row[key]))
                data_dict[row[key]] = row
        except csv.Error as e:
            module.fail_json(msg="Unable to process file: %s" % to_text(e))

    module.exit_json(dict=data_dict, list=data_list)