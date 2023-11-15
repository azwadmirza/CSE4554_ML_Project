def parse_call(expression, caller_context):
    src = expression['src']
    if caller_context.is_compact_ast:
        attributes = expression
        type_conversion = expression['kind'] == 'typeConversion'
        type_return = attributes['typeDescriptions']['typeString']

    else:
        attributes = expression['attributes']
        type_conversion = attributes['type_conversion']
        type_return = attributes['type']

    if type_conversion:
        type_call = parse_type(UnknownType(type_return), caller_context)

        if caller_context.is_compact_ast:
            assert len(expression['arguments']) == 1
            expression_to_parse = expression['arguments'][0]
        else:
            children = expression['children']
            assert len(children) == 2
            type_info = children[0]
            expression_to_parse = children[1]
            assert type_info['name'] in ['ElementaryTypenameExpression',
                                         'ElementaryTypeNameExpression',
                                         'Identifier',
                                         'TupleExpression',
                                         'IndexAccess',
                                         'MemberAccess']

        expression = parse_expression(expression_to_parse, caller_context)
        t = TypeConversion(expression, type_call)
        t.set_offset(src, caller_context.slither)
        return t

    call_gas = None
    call_value = None
    call_salt = None
    if caller_context.is_compact_ast:
        called = parse_expression(expression['expression'], caller_context)
        # If the next expression is a FunctionCallOptions
        # We can here the gas/value information
        # This is only available if the syntax is {gas: , value: }
        # For the .gas().value(), the member are considered as function call
        # And converted later to the correct info (convert.py)
        if expression['expression'][caller_context.get_key()] == 'FunctionCallOptions':
            call_with_options = expression['expression']
            for idx, name in enumerate(call_with_options.get('names', [])):
                option = parse_expression(call_with_options['options'][idx], caller_context)
                if name == 'value':
                    call_value = option
                if name == 'gas':
                    call_gas = option
                if name == 'salt':
                    call_salt = option
        arguments = []
        if expression['arguments']:
            arguments = [parse_expression(a, caller_context) for a in expression['arguments']]
    else:
        children = expression['children']
        called = parse_expression(children[0], caller_context)
        arguments = [parse_expression(a, caller_context) for a in children[1::]]

    if isinstance(called, SuperCallExpression):
        sp = SuperCallExpression(called, arguments, type_return)
        sp.set_offset(expression['src'], caller_context.slither)
        return sp
    call_expression = CallExpression(called, arguments, type_return)
    call_expression.set_offset(src, caller_context.slither)

    # Only available if the syntax {gas:, value:} was used
    call_expression.call_gas = call_gas
    call_expression.call_value = call_value
    call_expression.call_salt = call_salt
    return call_expression