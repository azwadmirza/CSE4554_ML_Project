def get_param_decl(param):

    def to_string(node):
        """Convert Doxygen node content to a string."""
        result = []
        for p in node.content_:
            value = p.value
            if not isinstance(value, six.text_type):
                value = value.valueOf_
            result.append(value)
        return ' '.join(result)

    param_type = to_string(param.type_)
    param_name = param.declname if param.declname else param.defname
    if not param_name:
        param_decl = param_type
    else:
        param_decl, number_of_subs = re.subn(r'(\([*&]+)(\))', r'\g<1>' + param_name + r'\g<2>',
                                             param_type)
        if number_of_subs == 0:
            param_decl = param_type + ' ' + param_name
    if param.array:
        param_decl += param.array
    if param.defval:
        param_decl += ' = ' + to_string(param.defval)

    return param_decl