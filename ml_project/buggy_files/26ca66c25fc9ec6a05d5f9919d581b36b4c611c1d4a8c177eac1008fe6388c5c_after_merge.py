def parse_expression(expression, caller_context):
    """

    Returns:
        str: expression
    """
    #  Expression
    #    = Expression ('++' | '--')
    #    | NewExpression
    #    | IndexAccess
    #    | MemberAccess
    #    | FunctionCall
    #    | '(' Expression ')'
    #    | ('!' | '~' | 'delete' | '++' | '--' | '+' | '-') Expression
    #    | Expression '**' Expression
    #    | Expression ('*' | '/' | '%') Expression
    #    | Expression ('+' | '-') Expression
    #    | Expression ('<<' | '>>') Expression
    #    | Expression '&' Expression
    #    | Expression '^' Expression
    #    | Expression '|' Expression
    #    | Expression ('<' | '>' | '<=' | '>=') Expression
    #    | Expression ('==' | '!=') Expression
    #    | Expression '&&' Expression
    #    | Expression '||' Expression
    #    | Expression '?' Expression ':' Expression
    #    | Expression ('=' | '|=' | '^=' | '&=' | '<<=' | '>>=' | '+=' | '-=' | '*=' | '/=' | '%=') Expression
    #    | PrimaryExpression

    # The AST naming does not follow the spec 
    name = expression[caller_context.get_key()]
    is_compact_ast = caller_context.is_compact_ast
    src = expression['src']

    if name == 'UnaryOperation':
        if is_compact_ast:
            attributes = expression
        else:
            attributes = expression['attributes']
        assert 'prefix' in attributes
        operation_type = UnaryOperationType.get_type(attributes['operator'], attributes['prefix'])

        if is_compact_ast:
            expression = parse_expression(expression['subExpression'], caller_context)
        else:
            assert len(expression['children']) == 1
            expression = parse_expression(expression['children'][0], caller_context)
        unary_op = UnaryOperation(expression, operation_type)
        unary_op.set_offset(src, caller_context.slither)
        return unary_op

    elif name == 'BinaryOperation':
        if is_compact_ast:
            attributes = expression
        else:
            attributes = expression['attributes']
        operation_type = BinaryOperationType.get_type(attributes['operator'])

        if is_compact_ast:
            left_expression = parse_expression(expression['leftExpression'], caller_context)
            right_expression = parse_expression(expression['rightExpression'], caller_context)
        else:
            assert len(expression['children']) == 2
            left_expression = parse_expression(expression['children'][0], caller_context)
            right_expression = parse_expression(expression['children'][1], caller_context)
        binary_op = BinaryOperation(left_expression, right_expression, operation_type)
        binary_op.set_offset(src, caller_context.slither)
        return binary_op

    elif name in 'FunctionCall':
        return parse_call(expression, caller_context)

    elif name == 'FunctionCallOptions':
        # call/gas info are handled in parse_call
        called = parse_expression(expression['expression'], caller_context)
        assert isinstance(called, (MemberAccess, NewContract))
        return called

    elif name == 'TupleExpression':
        """
            For expression like
            (a,,c) = (1,2,3)
            the AST provides only two children in the left side
            We check the type provided (tuple(uint256,,uint256))
            To determine that there is an empty variable
            Otherwhise we would not be able to determine that
            a = 1, c = 3, and 2 is lost

            Note: this is only possible with Solidity >= 0.4.12
        """
        if is_compact_ast:
            expressions = [parse_expression(e, caller_context) if e else None for e in expression['components']]
        else:
            if 'children' not in expression:
                attributes = expression['attributes']
                components = attributes['components']
                expressions = [parse_expression(c, caller_context) if c else None for c in components]
            else:
                expressions = [parse_expression(e, caller_context) for e in expression['children']]
        # Add none for empty tuple items
        if "attributes" in expression:
            if "type" in expression['attributes']:
                t = expression['attributes']['type']
                if ',,' in t or '(,' in t or ',)' in t:
                    t = t[len('tuple('):-1]
                    elems = t.split(',')
                    for idx in range(len(elems)):
                        if elems[idx] == '':
                            expressions.insert(idx, None)
        t = TupleExpression(expressions)
        t.set_offset(src, caller_context.slither)
        return t

    elif name == 'Conditional':
        if is_compact_ast:
            if_expression = parse_expression(expression['condition'], caller_context)
            then_expression = parse_expression(expression['trueExpression'], caller_context)
            else_expression = parse_expression(expression['falseExpression'], caller_context)
        else:
            children = expression['children']
            assert len(children) == 3
            if_expression = parse_expression(children[0], caller_context)
            then_expression = parse_expression(children[1], caller_context)
            else_expression = parse_expression(children[2], caller_context)
        conditional = ConditionalExpression(if_expression, then_expression, else_expression)
        conditional.set_offset(src, caller_context.slither)
        return conditional

    elif name == 'Assignment':
        if is_compact_ast:
            left_expression = parse_expression(expression['leftHandSide'], caller_context)
            right_expression = parse_expression(expression['rightHandSide'], caller_context)

            operation_type = AssignmentOperationType.get_type(expression['operator'])

            operation_return_type = expression['typeDescriptions']['typeString']
        else:
            attributes = expression['attributes']
            children = expression['children']
            assert len(expression['children']) == 2
            left_expression = parse_expression(children[0], caller_context)
            right_expression = parse_expression(children[1], caller_context)

            operation_type = AssignmentOperationType.get_type(attributes['operator'])
            operation_return_type = attributes['type']

        assignement = AssignmentOperation(left_expression, right_expression, operation_type, operation_return_type)
        assignement.set_offset(src, caller_context.slither)
        return assignement



    elif name == 'Literal':

        subdenomination = None

        assert 'children' not in expression

        if is_compact_ast:
            value = expression['value']
            if value:
                if 'subdenomination' in expression and expression['subdenomination']:
                    subdenomination = expression['subdenomination']
            elif not value and value != "":
                value = '0x' + expression['hexValue']
            type = expression['typeDescriptions']['typeString']

            # Length declaration for array was None until solc 0.5.5
            if type is None:
                if expression['kind'] == 'number':
                    type = 'int_const'
        else:
            value = expression['attributes']['value']
            if value:
                if 'subdenomination' in expression['attributes'] and expression['attributes']['subdenomination']:
                    subdenomination = expression['attributes']['subdenomination']
            elif value is None:
                # for literal declared as hex
                # see https://solidity.readthedocs.io/en/v0.4.25/types.html?highlight=hex#hexadecimal-literals
                assert 'hexvalue' in expression['attributes']
                value = '0x' + expression['attributes']['hexvalue']
            type = expression['attributes']['type']

        if type is None:
            if value.isdecimal():
                type = ElementaryType('uint256')
            else:
                type = ElementaryType('string')
        elif type.startswith('int_const '):
            type = ElementaryType('uint256')
        elif type.startswith('bool'):
            type = ElementaryType('bool')
        elif type.startswith('address'):
            type = ElementaryType('address')
        else:
            type = ElementaryType('string')
        literal = Literal(value, type, subdenomination)
        literal.set_offset(src, caller_context.slither)
        return literal

    elif name == 'Identifier':
        assert 'children' not in expression

        t = None

        if caller_context.is_compact_ast:
            value = expression['name']
            t = expression['typeDescriptions']['typeString']
        else:
            value = expression['attributes']['value']
            if 'type' in expression['attributes']:
                t = expression['attributes']['type']

        if t:
            found = re.findall('[struct|enum|function|modifier] \(([\[\] ()a-zA-Z0-9\.,_]*)\)', t)
            assert len(found) <= 1
            if found:
                value = value + '(' + found[0] + ')'
                value = filter_name(value)

        if 'referencedDeclaration' in expression:
            referenced_declaration = expression['referencedDeclaration']
        else:
            referenced_declaration = None

        var = find_variable(value, caller_context, referenced_declaration)

        identifier = Identifier(var)
        identifier.set_offset(src, caller_context.slither)
        return identifier

    elif name == 'IndexAccess':
        if is_compact_ast:
            index_type = expression['typeDescriptions']['typeString']
            left = expression['baseExpression']
            right = expression['indexExpression']
        else:
            index_type = expression['attributes']['type']
            children = expression['children']
            assert len(children) == 2
            left = children[0]
            right = children[1]
        # IndexAccess is used to describe ElementaryTypeNameExpression
        # if abi.decode is used
        # For example, abi.decode(data, ...(uint[]) )
        if right is None:
            return parse_expression(left, caller_context)

        left_expression = parse_expression(left, caller_context)
        right_expression = parse_expression(right, caller_context)
        index = IndexAccess(left_expression, right_expression, index_type)
        index.set_offset(src, caller_context.slither)
        return index

    elif name == 'MemberAccess':
        if caller_context.is_compact_ast:
            member_name = expression['memberName']
            member_type = expression['typeDescriptions']['typeString']
            member_expression = parse_expression(expression['expression'], caller_context)
        else:
            member_name = expression['attributes']['member_name']
            member_type = expression['attributes']['type']
            children = expression['children']
            assert len(children) == 1
            member_expression = parse_expression(children[0], caller_context)
        if str(member_expression) == 'super':
            super_name = parse_super_name(expression, is_compact_ast)
            var = find_variable(super_name, caller_context, is_super=True)
            if var is None:
                raise VariableNotFound('Variable not found: {}'.format(super_name))
            sup = SuperIdentifier(var)
            sup.set_offset(src, caller_context.slither)
            return sup
        member_access = MemberAccess(member_name, member_type, member_expression)
        member_access.set_offset(src, caller_context.slither)
        if str(member_access) in SOLIDITY_VARIABLES_COMPOSED:
            idx = Identifier(SolidityVariableComposed(str(member_access)))
            idx.set_offset(src, caller_context.slither)
            return idx
        return member_access

    elif name == 'ElementaryTypeNameExpression':
        return _parse_elementary_type_name_expression(expression, is_compact_ast, caller_context)


    # NewExpression is not a root expression, it's always the child of another expression
    elif name == 'NewExpression':

        if is_compact_ast:
            type_name = expression['typeName']
        else:
            children = expression['children']
            assert len(children) == 1
            type_name = children[0]

        if type_name[caller_context.get_key()] == 'ArrayTypeName':
            depth = 0
            while type_name[caller_context.get_key()] == 'ArrayTypeName':
                # Note: dont conserve the size of the array if provided
                # We compute it directly
                if is_compact_ast:
                    type_name = type_name['baseType']
                else:
                    type_name = type_name['children'][0]
                depth += 1
            if type_name[caller_context.get_key()] == 'ElementaryTypeName':
                if is_compact_ast:
                    array_type = ElementaryType(type_name['name'])
                else:
                    array_type = ElementaryType(type_name['attributes']['name'])
            elif type_name[caller_context.get_key()] == 'UserDefinedTypeName':
                if is_compact_ast:
                    array_type = parse_type(UnknownType(type_name['name']), caller_context)
                else:
                    array_type = parse_type(UnknownType(type_name['attributes']['name']), caller_context)
            elif type_name[caller_context.get_key()] == 'FunctionTypeName':
                array_type = parse_type(type_name, caller_context)
            else:
                raise ParsingError('Incorrect type array {}'.format(type_name))
            array = NewArray(depth, array_type)
            array.set_offset(src, caller_context.slither)
            return array

        if type_name[caller_context.get_key()] == 'ElementaryTypeName':
            if is_compact_ast:
                elem_type = ElementaryType(type_name['name'])
            else:
                elem_type = ElementaryType(type_name['attributes']['name'])
            new_elem = NewElementaryType(elem_type)
            new_elem.set_offset(src, caller_context.slither)
            return new_elem

        assert type_name[caller_context.get_key()] == 'UserDefinedTypeName'

        if is_compact_ast:
            contract_name = type_name['name']
        else:
            contract_name = type_name['attributes']['name']
        new = NewContract(contract_name)
        new.set_offset(src, caller_context.slither)
        return new

    elif name == 'ModifierInvocation':

        if is_compact_ast:
            called = parse_expression(expression['modifierName'], caller_context)
            arguments = []
            if expression['arguments']:
                arguments = [parse_expression(a, caller_context) for a in expression['arguments']]
        else:
            children = expression['children']
            called = parse_expression(children[0], caller_context)
            arguments = [parse_expression(a, caller_context) for a in children[1::]]

        call = CallExpression(called, arguments, 'Modifier')
        call.set_offset(src, caller_context.slither)
        return call

    raise ParsingError('Expression not parsed %s' % name)