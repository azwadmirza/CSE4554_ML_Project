def _calculate_binary_op(f, dataset, other, dest_vars, inplace=False,
                         drop_missing_vars=True):
    dataset_variables = getattr(dataset, 'variables', dataset)
    dataset_data_vars = getattr(dataset, 'data_vars', dataset)
    if utils.is_dict_like(other):
        other_variables = getattr(other, 'variables', other)
        other_data_vars = getattr(other, 'data_vars', other)
        performed_op = False
        for k in dataset_data_vars:
            if k in other_data_vars:
                dest_vars[k] = f(dataset_variables[k], other_variables[k])
                performed_op = True
            elif inplace and k in dest_vars:
                raise ValueError('datasets must have the same data variables '
                                 'for in-place arithmetic operations: %s, %s'
                                 % (list(dataset_data_vars),
                                    list(other_data_vars)))
            elif not drop_missing_vars:
                # this shortcuts left alignment of variables for fillna
                dest_vars[k] = dataset_variables[k]
        if not performed_op:
            raise ValueError('datasets have no overlapping data variables: '
                             '%s, %s' % (list(dataset_data_vars),
                                         list(other_data_vars)))
    else:
        other_variable = getattr(other, 'variable', other)
        for k in dataset_data_vars:
            dest_vars[k] = f(dataset_variables[k], other_variable)